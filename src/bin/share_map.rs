// 以模块的形式将字节码引入到程序中
mod share_map {
    include!(concat!(env!("OUT_DIR"), "/share_map.skel.rs"));
}

use std::{
    collections::BTreeMap,
    env,
    fs::{read_dir, read_to_string},
    os::unix::prelude::MetadataExt,
};

use anyhow::Ok;
use clap::{Args, Parser, Subcommand};
use libbpf_rs::{
    skel::{OpenSkel, SkelBuilder},
    MapFlags, PrintLevel,
};
use serde::{Deserialize, Serialize};
use share_map::*;

#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
struct VMInfo {
    pid: u64,
    kvm_debug_dir: String,
    cgroup: String,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct Config {
    vm_infos: BTreeMap<String, VMInfo>,
}

#[derive(Debug, Parser)]
struct Command {
    #[clap(short, long)]
    verbose: bool,

    #[clap(short, long)]
    idmode: bool,

    #[command(subcommand)]
    action: Action,
}

#[derive(Subcommand, Debug)]
enum Action {
    Insert(CommonArgs),
    Delete(CommonArgs),
    Get(CommonArgs),
    List,
    Clear,
    Apply {
        #[arg(short, long)]
        file: String,
    },
}

#[derive(Debug, Args)]
struct CommonArgs {
    cgroup: Vec<String>,
}

fn init_libbpf_log() {
    let log_level = if let Result::Ok(s) = env::var("LOG") {
        match s.as_str() {
            "DEBUG" => PrintLevel::Debug,
            _ => PrintLevel::Info,
        }
    } else {
        PrintLevel::Info
    };

    libbpf_rs::set_print(Some((
        log_level,
        |level: PrintLevel, msg: String| match level {
            PrintLevel::Debug => println!("{}", msg),
            _ => {}
        },
    )));
}

fn read_cgroup_inode_id(path: &str) -> anyhow::Result<u64> {
    println!("read cgroup: {}", path);
    let id = std::fs::metadata(path)?.ino();
    Ok(id)
}

#[derive(Debug)]
struct VMCgroup {
    emulator: String,
    vcpus: Vec<String>,
}

fn find_vm_cgroup(path: &str) -> anyhow::Result<VMCgroup> {
    let libvirt_path = path.to_owned() + "/libvirt";

    let mut vm_cgroup = VMCgroup {
        emulator: String::new(),
        vcpus: Vec::<String>::new(),
    };

    read_dir(libvirt_path)?.for_each(|dir| {
        if let Result::Ok(cgroup) = dir {
            let cgroup_path = cgroup.path().into_os_string().into_string().unwrap();
            let cgroup_name = cgroup.file_name().into_string().unwrap();

            if cgroup_name == "emulator" {
                vm_cgroup.emulator = cgroup_path;
            } else if cgroup_name.starts_with("vcpu") {
                vm_cgroup.vcpus.push(cgroup_path);
            }
        }
    });

    Ok(vm_cgroup)
}

#[cfg(test)]
mod test {
    use crate::find_vm_cgroup;

    #[test]
    fn read_vm_cgroup() {
        let dummy_path = "/tmp/test_vm";

        let vm_cgroup = find_vm_cgroup(dummy_path);

        println!("{:#?}", vm_cgroup);
    }
}

fn main() -> anyhow::Result<()> {
    init_libbpf_log();
    let opts = Command::parse();

    let mut skel_builder = ShareMapSkelBuilder::default();
    if opts.verbose {
        skel_builder.obj_builder.debug(true);
    }

    let open_skel = skel_builder.open()?;
    let skel = open_skel.load()?;
    let maps = skel.maps();
    let cgroup_map = maps.cgroup_map();

    match opts.action {
        Action::Insert(args) => args.cgroup.into_iter().for_each(|path| {
            if let Result::Ok(cg_id) = read_cgroup_inode_id(&path) {
                let cgroup_id = cg_id.to_le_bytes();
                cgroup_map
                    .update(&cgroup_id, &cgroup_id, MapFlags::NO_EXIST)
                    .expect("insert element to map failed");
            };
        }),
        Action::Delete(args) => args.cgroup.into_iter().for_each(|path| {
            if let Result::Ok(cg_id) = read_cgroup_inode_id(&path) {
                let cgroup_id = cg_id.to_le_bytes();
                cgroup_map
                    .delete(&cgroup_id)
                    .expect("delete element from map failed");
            };
        }),
        Action::Get(args) => args.cgroup.into_iter().for_each(|path| {
            if let Result::Ok(cg_id) = read_cgroup_inode_id(&path) {
                let cgroup_id = cg_id.to_le_bytes();
                let _ = cgroup_map
                    .lookup(&cgroup_id, MapFlags::ANY)
                    .expect("get element from map failed")
                    .is_some_and(|val| {
                        let mut cgroup_id: u64 = 0;
                        plain::copy_from_bytes(&mut cgroup_id, &val).expect("data not long enough");
                        println!("key: {}, val: {}", cg_id, cgroup_id);
                        true
                    });
            };
        }),
        Action::List => cgroup_map.keys().for_each(|k| {
            let _ = cgroup_map
                .lookup(&k, MapFlags::ANY)
                .unwrap()
                .is_some_and(|val| {
                    let mut key: u64 = 0;
                    let mut cgroup_id: u64 = 0;
                    plain::copy_from_bytes(&mut key, &k).expect("data not long enough");
                    plain::copy_from_bytes(&mut cgroup_id, &val).expect("data not long enough");

                    println!("key: {}, val: {}", key, cgroup_id);
                    true
                });
        }),
        Action::Clear => cgroup_map.keys().for_each(|k| {
            cgroup_map
                .delete(&k)
                .expect("delete element from map failed");
        }),
        Action::Apply { file } => {
            let yaml = read_to_string(file).unwrap();
            let config: Config = serde_yaml::from_str(&yaml).unwrap();

            config.vm_infos.iter().for_each(|(_, vm_info)| {
                let vm_cgroup = find_vm_cgroup(&vm_info.cgroup).expect("not a valid vm cgroup");

                if let Result::Ok(cg_id) = read_cgroup_inode_id(&vm_cgroup.emulator) {
                    let cgroup_id = cg_id.to_le_bytes();
                    cgroup_map
                        .update(&cgroup_id, &cgroup_id, MapFlags::NO_EXIST)
                        .expect("insert element to map failed");
                };

                vm_cgroup.vcpus.iter().for_each(|cgroup| {
                    if let Result::Ok(cg_id) = read_cgroup_inode_id(cgroup) {
                        let cgroup_id = cg_id.to_le_bytes();
                        cgroup_map
                            .update(&cgroup_id, &cgroup_id, MapFlags::NO_EXIST)
                            .expect("insert element to map failed");
                    };
                })
            })
        }
    }

    Ok(())
}

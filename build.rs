use libbpf_cargo::SkeletonBuilder;
use regex::Regex;
use std::{env, fs, path::PathBuf};

const BPF_DIR: &str = "src/bpf/";

fn main() {
    let out_dir =
        PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR must be set in build script"));

    let builder = |src_name: &str, pj_name: &str| {
        let mut src = String::from(BPF_DIR);
        let mut out = out_dir.clone();

        src.push_str(src_name);
        out.push(&format!("{}.skel.rs", pj_name));

        SkeletonBuilder::new()
            .source(&src)
            .build_and_generate(&out)
            .unwrap();
        println!("cargo:return-if-changed={}", src);
    };

    let paths = fs::read_dir(BPF_DIR).expect("read dir failed");
    let re = Regex::new(r"(.*).bpf.c").unwrap();

    for path in paths {
        if let Ok(entry) = path {
            if let Some(filename) = entry.file_name().to_str() {
                if let Some(caps) = re.captures(filename) {
                    if let Some(pj_name) = caps.get(1) {
                        builder(filename, pj_name.as_str());
                    }
                }
            }
        }
    }
}

#[test]
mod test {
    use regex::Regex;

    #[test]
    fn get_pj_name() {
        let re = Regex::new(r"(.*).bpf.c").unwrap();
        let file_name = "hello.bpf.c";
        let caps = re.captures(file_name).unwrap();

        assert!(caps.get(1).unwrap().as_str(), "hello");
    }
}

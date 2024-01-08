package cmd

import (
	"net/http"
	"strings"

	"github.com/Faione/easyxporter"
	_ "github.com/Faione/resctrl_exporter/collectors"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

const (
	keyWebListenAddress = "web.listen-address"
	keyWebTelemetryPath = "web.telemetry-path"
	keyWebMaxRequests   = "web.max-requests"

	keyDebug    = "debug"
	keyLogLevel = "log"
)

func New() *cobra.Command {
	vp := newViper()
	rootCmd := &cobra.Command{
		Use:   "resctrl_exporter ",
		Short: "Resctrl Exporter",
		Long:  "Resctrl Exporter",
		RunE: func(cmd *cobra.Command, args []string) error {
			if err := runExporter(vp, args); err != nil && err != http.ErrServerClosed {
				return err
			}
			return nil
		},
	}

	flags := rootCmd.Flags()
	flags.String(
		keyWebListenAddress,
		":9900",
		"Address on which to expose metrics and web interface.",
	)
	flags.String(
		keyWebTelemetryPath,
		"/metrics",
		"Path under which to expose metrics.",
	)
	flags.Int(
		keyWebMaxRequests,
		40,
		"Maximum number of parallel scrape requests. Use 0 to disable.",
	)
	flags.BoolP(
		keyDebug,
		"d",
		false,
		"Set loglevel to Debug",
	)

	flags.AddFlagSet(easyxporter.Flags())
	vp.BindPFlags(flags)
	return rootCmd
}

func newViper() *viper.Viper {
	vp := viper.New()
	vp.SetEnvPrefix("se")
	vp.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	vp.AutomaticEnv()
	return vp
}

func newLogger(level string) *logrus.Logger {
	logger := logrus.New()
	switch level {
	case "ERROR":
		logger.SetLevel(logrus.ErrorLevel)
	case "WARN":
		logger.SetLevel(logrus.WarnLevel)
	case "DEBUG":
		logger.SetLevel(logrus.DebugLevel)
	case "TRACE":
		logger.SetLevel(logrus.TraceLevel)
	default:
		logger.SetLevel(logrus.InfoLevel)
	}

	return logger
}

func runExporter(vp *viper.Viper, args []string) error {

	var (
		listenAddress = vp.GetString(keyWebListenAddress)
		metricsPath   = vp.GetString(keyWebTelemetryPath)
		maxRequests   = vp.GetInt(keyWebMaxRequests)
		logLevel      = vp.GetString(keyLogLevel)
		debug         = vp.GetBool(keyDebug)
	)

	if debug {
		logLevel = "DEBUG"
	}
	logger := newLogger(logLevel)
	logger.Debug("init server ->", " metricsPath: ", metricsPath, " listenAddress: ", listenAddress, "log: ", logLevel)

	return easyxporter.Build(
		listenAddress,
		"resctrl",
		easyxporter.WithMetricPath(metricsPath),
		easyxporter.WithMaxRequests(maxRequests),
		easyxporter.WithLogger(logger),
	).Run()

}

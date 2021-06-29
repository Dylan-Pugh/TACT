import subprocess

from tact.control.logging_controller import \
    LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def compile_args_string(settings_JSON):
    logger.info("Creating flat args array from input")

    args = []

    args.insert(0, settings_JSON["eddType"])

    for current in settings_JSON["parameters"]:
        args.insert(current["position"], current["value"])

    args_string = " "
    return args_string.join(args)


def invoke(settings_JSON):
    logger.info("Compiling Bash command to call Java class: GenerateDatasetsXml")

    bash_command = "java -cp classes:" + \
        settings_JSON["erddapPath"] + "lib/servlet-api.jar:lib/* -Xms1000M -Xmx1000M gov.noaa.pfel.erddap.GenerateDatasetsXml " + compile_args_string(settings_JSON)

    logger.info("Compiled command: %s", bash_command)

    try:
        result = subprocess.run(
            bash_command.split(),
            capture_output=True,
            text=True,
            check=True)

        logger.info("stdout: from GenerateDatasetsXml.java: %s", result.stdout)
        logger.error(
            "stderr: from GenerateDatasetsXml.java: %s",
            result.stderr)

    except ValueError as ex:
        logger.error(ex.message)

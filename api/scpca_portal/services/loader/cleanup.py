import shutil


class Cleanup():
    def clean_up_data(self):
        if samples_count := self.project.samples.count():
            logger.info(
                f"Created {samples_count} sample{pluralize(samples_count)} for '{self.project}'"
            )

        if kwargs["clean_up_input_data"]:
            logger.info(f"Cleaning up '{project}' input data")
            self.clean_up_input_data()

        if kwargs["clean_up_output_data"]:
            logger.info("Cleaning up output directory")
            self.clean_up_output_data()

    def clean_up_input_data(self):
        shutil.rmtree(common.INPUT_DATA_PATH / self.project.scpca_id, ignore_errors=True)

    @staticmethod
    def clean_up_output_data():
        for path in Path(common.OUTPUT_DATA_PATH).glob("*"):
            path.unlink(missing_ok=True)

# Copyright 2024 Broadcom. All Rights Reserved.
import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Racetrack:
    def __init__(self, test_set_id=None, result_id=None):
        self.test_set_id = test_set_id
        self.test_case_result = None
        self.result_id = result_id
        self.RESULT_TYPES = ["PASS", "FAIL", "RUNNING", "CONFIG", "SCRIPT", "PRODUCT", "RERUNPASS", "UNSUPPORTED"]

    # Allowed result types

    # Function to make post requests to racetrack server
    def _post(self, method, data):
        # Do not post the test result test_set_id is None at local appliance since it will be posted during merge.
        if not self.test_set_id:
            return
        url = "https://racetrack.eng.vmware.com/{}".format(method)
        # Remove any values from data that are empty
        for key in list(data.keys()):
            if not data[key]:
                del data[key]
            else:
                # Encode data for post request
                if isinstance(data[key], str):
                    data[key] = data[key].encode("utf-8")
        return requests.post(url, data=data)

    def test_set_begin(
        self,
        build_id,
        user,
        product,
        description,
        host_os,
        server_build_id=None,
        branch=None,
        build_type=None,
        test_type=None,
        language=None,
    ):
        """test_set_begin - begin a new test set in Racetrack.

        Param            Required? Description
        build_id         Yes       The build number that is being tested
        user             Yes       The user running the test
        product          Yes       The name of the product under test
        description      Yes       A description of this test run
        host_os          Yes       The Host OS
        server_build_id  No        The build number of the "server" product
        branch           No        The branch which generated the build
        build_type       No        The type of build under test
        test_type        No        default Regression
        language         No        default English
        """
        data = {
            "BuildID": build_id,
            "User": user,
            "Product": product,
            "Description": description,
            "HostOS": host_os,
            "ServerBuildID": server_build_id,
            "Branch": branch,
            "BuildType": build_type,
            "TestType": test_type,
            "Language": language,
        }

        response = self._post("TestSetBegin.php", data)
        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occurred while creating the test set: \n {}".format(response.text))
            return status

        self.test_set_id = response.text
        logger.info("\n Test set with id {} created successfully".format(response.text))

        return status

    # Creates a new test_case within a racetrack, the id is stored for updating the test case
    def test_case_begin(
        self,
        name,
        feature,
        description=None,
        machine_name=None,
        tcmsid=None,
        input_language=None,
        gos=None,
        start_time=None,
    ):
        """test_case_begin - begin a new test case in Racetrack.

        Param            Required? Description
        name             Yes       The name of the test case
        feature          Yes       The feature that is being tested
        description      No        A description of this test case (defaults to whatever was provided for Name).
        machine_name     No        The Host OS
        tcmsid           No        A comma-separated set of values that correspond to the Test Case Management System Id's (TCMSID) of this test case.
        input_language   No        The two letter abbreviation for the language used (e.g. 'EN', 'JP').
        gos              No        The guest operating system
        start_time       No        If not provided, current time is used.
        """
        if not self.test_set_id:
            return False
        data = {
            "ResultSetID": self.test_set_id,
            "Name": name,
            "Feature": feature,
            "Description": description,
            "MachineName": machine_name,
            "TCMSID": tcmsid,
            "InputLanguage": input_language,
            "GOS": gos,
            "StartTime": start_time,
        }

        response = self._post("TestCaseBegin.php", data)
        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occurred while creating new testcase: \n {}".format(response.text))
            return status

        self.result_id = response.text

        logger.info("\n Test case initiated successfully with ResultId {}".format(response.text))

        return status

    # Adds a comment to the current testcase
    def comment(self, comment):
        if not self.test_set_id:
            return False
        """comment - submit a comment for a test case.

           Param          Required?   Description
           description    Yes         The comment
        """
        data = {"ResultID": self.result_id, "Description": comment}

        response = self._post("TestCaseComment.php", data)
        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occurred while updating racetrack: \n {}".format(response.text))
            return status

        logger.info("\n Racetrack updated successfully")

        return status

    # Adds a warning to the current test case
    def warning(self, warning):
        if not self.test_set_id:
            return False
        """warning - submit a warning for a test case.

           Param          Required?   Description
           description    Yes         The warning
        """
        data = {"ResultID": self.result_id, "Description": warning}

        response = self._post("TestCaseWarning.php", data)
        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occurred while updating racetrack: \n {}".format(response.text))
            return status

        logger.info("\n Racetrack updated successfully")

        return status

    # Updates the test case with expexted, actual, and result of a verification
    def verify(self, description, actual, expected):
        if not self.test_set_id:
            return False
        """verify - Validate the actual matches the expected.

           Param          Required?   Description
           description    Yes         The comment
           actual         Yes         The actual value. (any string)
           expected       Yes         The expected value. (any string)
        """
        if actual == expected:
            result = "TRUE"
        else:
            result = "FALSE"

        data = {
            "Description": description,
            "Actual": actual,
            "Expected": expected,
            "Result": result,
            "ResultID": self.result_id,
        }

        response = self._post("TestCaseVerification.php", data)
        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occured while updating racetrack: \n {}".format(response.text))
            return status

        logger.info("\n Racetrack updated successfully")

        return status

    def test_case_end(self, result):
        if not self.test_set_id:
            return False

        """
        Ends a test case, the result of the testcase needs to be provided.
        Valid inputs are
        ['PASS', 'FAIL', 'RUNNING', 'CONFIG', 'SCRIPT', 'PRODUCT','RERUNPASS', 'UNSUPPORTED']
         """
        if result not in self.RESULT_TYPES:
            logger.error(
                "\n Specified test result is invalid, please use one of the supported types \n {}".format(
                    self.RESULT_TYPES
                )
            )
            return False
        data = {"Result": result, "ID": self.result_id}

        response = self._post("TestCaseEnd.php", data)
        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occured while ending testcase: \n {}".format(response.text))
            return status

        logger.info("\n Testcase ended successfully")

        return status

    def test_set_end(self):
        if not self.test_set_id:
            return False

        # Ends the testset
        data = {"ID": self.test_set_id}

        response = self._post("TestSetEnd.php", data)

        status = bool(response.status_code == 200)

        if not status:
            logger.error("\n An error occured while ending the test set: \n {}".format(response.text))
            return status

        logger.info("\n Test set ended successfully")

        return status

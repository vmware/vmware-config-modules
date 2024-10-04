# Copyright 2024 Broadcom. All Rights Reserved.
import enum
from typing import List

from pydantic import BaseModel


class BaseResponseModel(BaseModel):
    """Class to represent a base response model."""

    def to_dict(self, strip_null=True) -> dict:
        """
        Returns the model properties as a dict
        :param strip_null: remove attributes with null values
        :rtype: dict
        """
        result_dict = {}
        for key, value in vars(self).items():
            if strip_null and value is None:
                continue
            if isinstance(value, List):
                if len(value) > 0:
                    result_dict[key] = list(map(lambda x: x.to_dict(strip_null) if hasattr(x, "to_dict") else x, value))
            elif isinstance(value, enum.Enum):
                result_dict[key] = value.value
            elif hasattr(value, "to_dict"):
                nested_dict_value = value.to_dict(strip_null)
                if nested_dict_value:
                    result_dict[key] = nested_dict_value
            elif isinstance(value, dict):
                result_dict[key] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict(strip_null)) if hasattr(item[1], "to_dict") else item,
                        value.items(),
                    )
                )
            else:
                result_dict[key] = str(value)
        return result_dict

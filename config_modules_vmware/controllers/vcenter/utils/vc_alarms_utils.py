# Copyright 2024 Broadcom. All Rights Reserved.
import logging
import re
from typing import Dict
from typing import List

from pyVmomi import vim  # pylint: disable=E0401

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

# Alarm info consts
ALARM_NAME = "alarm_name"
ALARM_DESCRIPTION = "alarm_description"
ENABLED = "enabled"
TARGET_TYPE = "target_type"
RULE_EXPRESSIONS = "rule_expressions"
ALARM_ACTIONS = "alarm_actions"

# Expression consts
EVENT_TYPE_ID = "event_type_id"
COMPARISONS = "comparisons"

# Expression comparisons consts
ATTRIBUTE = "attribute"
OPERATOR = "operator"
VALUE = "value"

# Severity level consts
CRITICAL = "CRITICAL"
WARNING = "WARNING"
NORMAL = "NORMAL"

# Severity color codes consts
RED = "red"
YELLOW = "yellow"
GREEN = "green"

# Action type consts
ACTION_TYPE = "action_type"
EMAIL_ACTION = "EMAIL"
SNMP_ACTION = "SNMP"
SCRIPT_ACTION = "SCRIPT"

# Action details consts
EMAIL = "email"
TO_LIST = "to_list"
CC_LIST = "cc_list"
BODY = "body"
SUBJECT = "subject"
SCRIPT_NAME = "script_name"

# Other consts
STATE = "state"
REPEAT = "repeats"
ACTION_FREQUENCY = "action_frequency"

COLOR_TO_SEVERITY_MAP = {"red": "CRITICAL", "yellow": "WARNING", "green": "NORMAL"}
SEVERITY_TO_COLOR_MAP = {"CRITICAL": "red", "WARNING": "yellow", "NORMAL": "green", "NO_CHANGE": None}

TARGET_TO_CLASS_NAME_MAP = {
    "VCENTER": vim.Folder,
    "HOSTS": vim.HostSystem,
    "CLUSTERS": vim.ClusterComputeResource,
    "DATACENTERS": vim.Datacenter,
    "DATASTORES": vim.Datastore,
    "DISTRIBUTED_SWITCHES": vim.DistributedVirtualSwitch,
    "DISTRIBUTED_PORT_GROUPS": vim.dvs.DistributedVirtualPortgroup,
    "VIRTUAL_MACHINES": vim.VirtualMachine,
    "DATASTORE_CLUSTERS": vim.StoragePod,
}

CLASS_NAME_TO_TARGET_MAP = {
    "vim.Folder": "VCENTER",
    "vim.HostSystem": "HOSTS",
    "vim.ClusterComputeResource": "CLUSTERS",
    "vim.Datacenter": "DATACENTERS",
    "vim.Datastore": "DATASTORES",
    "vim.DistributedVirtualSwitch": "DISTRIBUTED_SWITCHES",
    "vim.dvs.DistributedVirtualPortgroup": "DISTRIBUTED_PORT_GROUPS",
    "vim.VirtualMachine": "VIRTUAL_MACHINES",
    "vim.StoragePod": "DATASTORE_CLUSTERS",
}


def get_comparisons_for_expression(
    expression: vim.alarm.EventAlarmExpression,
) -> List[vim.alarm.EventAlarmExpression.Comparison]:
    """
    Return a list of comparison for the given expression
    :param expression: Expression in an alam.
    :type expression: vim.alarm.EventAlarmExpression
    :return: List of comparison
    :rtype: List[vim.alarm.EventAlarmExpression.Comparison]
    """
    comparisons = []
    for item in expression.comparisons:
        comparisons.append({ATTRIBUTE: item.attributeName, OPERATOR: item.operator, VALUE: item.value})
    return comparisons


def get_target_type(object_type) -> str:
    """
    Get target type from the given class object.
    :param object_type: vim Object for vcenter, hosts, datacenter etc
    :type: vim.Folder or vim.HostSystem etc
    :return: target product name
    :rtype: str
    """
    logger.info(f"Target object type is {object_type}.")
    str_object_type = str(object_type)
    match = re.search(r"<class 'pyVmomi.VmomiSupport.(.+?)'>", str_object_type)
    if match:
        str_object_type = match.group(1)
    target_type = CLASS_NAME_TO_TARGET_MAP[str_object_type]
    if not target_type:
        target_type = "VCENTER"
    return target_type


def get_alarm_details(alarm_def: vim.alarm.Alarm, target_type: str) -> Dict:
    """
    Get alarm details for the given alarm_def object and for a given target_type
    :param alarm_def: Alarm definition holding alarm info.
    :type alarm_def: vim.alarm.Alarm
    :param target_type: Target product for the alarm
    :type: str
    :return: Dictionary with alarm details - with keys 'alarm_name', 'alarm_description', 'rule_expressions' etc.
    :rtype: dict
    """
    logger.info(f"Get alarm details for {alarm_def}: {alarm_def.info.name}")
    result = {}
    alarm_info = alarm_def.info
    result[ALARM_NAME] = alarm_def.info.name
    result[ALARM_DESCRIPTION] = alarm_def.info.description
    result[ENABLED] = alarm_def.info.enabled
    result[TARGET_TYPE] = target_type
    result[RULE_EXPRESSIONS] = []
    result[ACTION_FREQUENCY] = alarm_def.info.actionFrequency
    for expression in alarm_info.expression.expression:
        if isinstance(expression, vim.alarm.EventAlarmExpression):
            rule = {
                STATE: None if expression.status is None else COLOR_TO_SEVERITY_MAP[expression.status],
                EVENT_TYPE_ID: expression.eventTypeId,
                COMPARISONS: get_comparisons_for_expression(expression),
            }
            result[RULE_EXPRESSIONS].append(rule)
    if hasattr(alarm_info.action, "action"):
        result[ALARM_ACTIONS] = []
        for action in alarm_info.action.action:
            action_result = {
                STATE: COLOR_TO_SEVERITY_MAP[action.transitionSpecs[0].finalState],
                REPEAT: action.transitionSpecs[0].repeats,
            }
            if isinstance(action.action, vim.action.SendEmailAction):
                action_result[ACTION_TYPE] = EMAIL_ACTION
                action_result[EMAIL] = {
                    SUBJECT: action.action.subject,
                    TO_LIST: action.action.toList,
                    CC_LIST: action.action.ccList,
                    BODY: action.action.body,
                }
            elif isinstance(action.action, vim.action.RunScriptAction):
                action_result[ACTION_TYPE] = SCRIPT_ACTION
                action_result[SCRIPT_NAME] = action.action.script
            elif isinstance(action.action, vim.action.SendSNMPAction):
                action_result[ACTION_TYPE] = SNMP_ACTION
            result[ALARM_ACTIONS].append(action_result)
    return result


def build_transitions_for_alarm(start: str, final: str, repeat: bool) -> vim.alarm.AlarmTriggeringAction.TransitionSpec:
    """
    Create transition specs for the alarm for given start, final and repeats.
    :param start: Color code for the start severity state.
    :type start: str
    :param final: Color code for the start severity state.
    :type final: str
    :param repeat: Flag to denote whether action is to be repeated or not.
    :type repeat: bool
    :return: Transition spec object
    :rtype: vim.alarm.AlarmTriggeringAction.TransitionSpec
    """
    transition = vim.alarm.AlarmTriggeringAction.TransitionSpec()
    transition.startState = start
    transition.finalState = final
    transition.repeats = repeat
    return transition


def create_alarm_spec(desired_values: dict, target_event_id: str) -> vim.alarm.AlarmSpec:
    """
    Create alarm spec with desired values for the alarm.
    :param desired_values: Dictionary of alarm details.
    :type desired_values: dict
    :param target_event_id: Target event id for the particular alarm
    :type target_event_id: str
    :return: Alarm spec with populated alarm details.
    :rtype: vim.alarm.AlarmSpec
    """

    logger.info(f"Create alarm spec for {desired_values.get(ALARM_NAME)}.")
    spec = vim.alarm.AlarmSpec()
    spec.expression = vim.alarm.OrAlarmExpression()
    spec.name = desired_values.get(ALARM_NAME)
    spec.description = desired_values.get(ALARM_DESCRIPTION, "")
    spec.enabled = desired_values.get(ENABLED)
    spec.setting = vim.alarm.AlarmSetting()
    spec.setting.toleranceRange = 0
    spec.setting.reportingFrequency = 300
    if ACTION_FREQUENCY in desired_values:
        spec.actionFrequency = desired_values.get(ACTION_FREQUENCY)
    rule_expressions = desired_values.get(RULE_EXPRESSIONS)
    temp_expressions = []
    is_target_event_id_present = False

    # Populate rule_expressions in the alarm spec
    for rule_expression in rule_expressions:
        event_type_id = rule_expression.get(EVENT_TYPE_ID)
        if event_type_id == target_event_id:
            is_target_event_id_present = True
        temp_expression = vim.alarm.EventAlarmExpression()
        temp_expression.eventTypeId = event_type_id
        temp_expression.eventType = vim.event.Event
        temp_expression.objectType = TARGET_TO_CLASS_NAME_MAP[desired_values.get(TARGET_TYPE)]
        temp_expression.status = SEVERITY_TO_COLOR_MAP[rule_expression.get(STATE)]
        if COMPARISONS in rule_expression:
            temp_comparisons = []
            for comparison in rule_expression.get(COMPARISONS):
                temp_comparison = vim.alarm.EventAlarmExpression.Comparison()
                temp_comparison.attributeName = comparison.get(ATTRIBUTE)
                temp_comparison.operator = comparison.get(OPERATOR)
                temp_comparison.value = comparison.get(VALUE)
                temp_comparisons.append(temp_comparison)
            temp_expression.comparisons = temp_comparisons
        temp_expressions.append(temp_expression)
    if is_target_event_id_present is False:
        raise Exception(f"Need {target_event_id} as eventTypeId at least for one of the expression")

    if temp_expressions:
        spec.expression.expression = temp_expressions

    # Populate alarm actions in the alarm spec.
    actions = desired_values.get(ALARM_ACTIONS)
    if actions:
        spec.action = vim.alarm.GroupAlarmAction()
        temp_actions = []
        for action in actions:
            temp_action = vim.alarm.AlarmTriggeringAction()
            temp_action.yellow2green = False
            temp_action.yellow2red = False
            temp_action.red2yellow = False
            temp_action.green2yellow = False
            temp_action.transitionSpecs = []
            if action.get(STATE) == WARNING:
                temp_action.transitionSpecs.append(
                    build_transitions_for_alarm(start=RED, final=YELLOW, repeat=action.get(REPEAT))
                )
                temp_action.transitionSpecs.append(
                    build_transitions_for_alarm(start=GREEN, final=YELLOW, repeat=action.get(REPEAT))
                )
            elif action.get(STATE) == CRITICAL:
                temp_action.transitionSpecs.append(
                    build_transitions_for_alarm(start=YELLOW, final=RED, repeat=action.get(REPEAT))
                )
            elif action.get(STATE) == NORMAL:
                temp_action.transitionSpecs.append(
                    build_transitions_for_alarm(start=YELLOW, final=GREEN, repeat=action.get(REPEAT))
                )
            else:
                temp_action.transitionSpecs.append(
                    build_transitions_for_alarm(start=RED, final=YELLOW, repeat=action.get(REPEAT))
                )

            action_type = action.get(ACTION_TYPE)
            if action_type == EMAIL_ACTION:
                email_action = vim.action.SendEmailAction()
                email_info = action.get(EMAIL, {})
                email_action.subject = email_info.get(SUBJECT, "")
                email_action.toList = email_info.get(TO_LIST, "")
                email_action.ccList = email_info.get(CC_LIST, "")
                email_action.body = email_info.get(BODY, "")
                temp_action.action = email_action
            elif action_type == SNMP_ACTION:
                snmp_action = vim.action.SendSNMPAction()
                temp_action.action = snmp_action
            elif action_type == SCRIPT_ACTION:
                script_action = vim.action.RunScriptAction()
                script_action.script = action.get(SCRIPT_NAME, "")
                temp_action.action = script_action
            else:
                logger.error(f"Unexpected action type {action_type}.")
            temp_actions.append(temp_action)

        if temp_actions:
            spec.action.action = temp_actions
    return spec

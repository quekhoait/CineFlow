from app import db
from app.dto.rule_dto import RulesDTO
from app.repository import rule_repo

def update(data: RulesDTO):
    updated_keys = []
    for item in data:
        rule_key = item.name
        rule_value = item.value
        rule = rule_repo.update_rules(rule_key, rule_value)
        updated_keys.append(rule)
    db.session.commit()

def rules():
    rules = rule_repo.get_rules_by_names()
    return RulesDTO(many=True).dump(rules)
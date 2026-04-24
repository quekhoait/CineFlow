from app.models import Rules

def update_rules(key, value):
    rule = Rules.query.filter_by(name=key, active=True).first()
    if rule: rule.value = value
    return rule

def get_rules_by_names():
    rules = Rules.query.filter(Rules.active==True).all()
    return rules
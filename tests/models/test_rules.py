import pytest
from sqlalchemy.exc import IntegrityError
from app.models.rules import Rules

class TestRulesModel:
    def test_rules_default_values(self, test_session, test_setup_user):
        rule = Rules(
            name="Weekend Surcharge",
            type="PRICE_MODIFIER",
            value="1.2",
            user_id=test_setup_user.id
        )
        test_session.add(rule)
        test_session.commit()

        #kiểm tra default và bool
        assert rule.active is True

    def test_rules_missing_user_id(self, test_session):
        invalid_rule = Rules(
            name="Holiday Surcharge",
            type="PRICE",
            value="50000"
            #thiếu user_id
        )
        test_session.add(invalid_rule)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()
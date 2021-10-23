# -*- coding: utf-8 -*-
{
    'name': "Checks Workflow",
    'summary': "Checks Workflow",
    'version': '0.1',
    'depends': ['base','account_check_printing','account_payment'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'wizard/cancel_reason_wizard.xml',
        'views/account_journal_inherit_view.xml',
        'views/account_payment_inherit_view.xml',
        'views/account_payment_actions.xml',
        'views/menu_item_view.xml',
    ],
}

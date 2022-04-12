query = pm, cb, i, pf

def fetch_from_list(rules, **params):
    for r in product(
        {params.get('payment_method'), None},
        {params.get('card_brand'), None},
        {params.get('installment'), None},
        {params.get('payment_flow'), None},
    ):
        if {
            'payment_method': r[0],
            'card_brand': r[1],
            'installment': r[2],
            'payment_flow': r[3],
        } in rules:
            return True

rules = map(
    lambda r: {
        k: r[k]
        for k in (
            'payment_method',
            'card_brand',
            'installment',
            'payment_flow',
        )
    },
    rules_as_dict
)
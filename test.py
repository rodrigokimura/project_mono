select
    distinct
    sr.*,
    p.blocked as blocked
from
    split_rule sr
join order_split_rule osr on sr.id = osr.splitrule_id
join recipient r on sr.recipient_id = r.id
join "order" o on osr.order_id = o.id
join "transaction" t on t.order_id  = o.id
join payable p on r.id = p.recipient_id and t.id = p.transaction_id
where 1=1
    {f" and r.reference_key = '{recipient_ref_key}' " if recipient_ref_key else ''}
    {f" and r.public_id = '{recipient_id}' " if recipient_id else ''}
    and o.reference_key = '{order_ref_key}'
    and o.org_id = {org.id}

orders__transaction
SplitRule.obkects.filter(
    order__transaction__payable__recipient=
)


filters = {
    'order__reference_key': order_ref_key,
    'order__org_id': org.id,
}
if recipient_ref_key:
    filters['recipient__reference_key'] = recipient_ref_key
if recipient_id:
    filters['recipient__public_id'] = recipient_id

split_rules = (
    SplitRule.objects.filter(**filters)
    .annotate(
        blocked=Subquery(
            Payable.objects.filter(
                recipient_id=OuterRef(
                    'order__transaction__payable__recipient_id'
                ),
                transaction_id=OuterRef(
                    'order__transaction_id'
                )
            ).values('blocked')[:1]
        )
    )
    .filter(blocked__isnull=False)
    .distinct()
)
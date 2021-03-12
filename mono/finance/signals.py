from .models import Configuration, Group, Account, Category, Icon

def initial_setup(sender, instance, created, **kwargs):
    
    INITIAL_CATEGORIES = [
        ['Health', 'EXP', 'heartbeat'], 
        ['Shopping', 'EXP', 'cart'], 
        ['Education', 'EXP', 'university'],
        ['Transportation', 'EXP', 'car'],
        ['Trips', 'EXP', 'plane'],
        ['Leisure', 'EXP', 'gamepad'],
        ['Groceries', 'EXP', 'shopping basket'],
        ['Salary', 'INC', 'money bill alternate outline'],
    ]
    
    if created:
        try:
            instance.groups.add(Group.objects.get(name='Cliente'))
        except Group.DoesNotExist:
            pass
        
        # Initial accounts
        Account.objects.create(name="Wallet", owned_by=instance, created_by=instance)
        Account.objects.create(name="Bank", owned_by=instance, created_by=instance)
        
        #Initial categories
        for category in INITIAL_CATEGORIES:
            Category.objects.create(
                name=category[0],
                type=category[1],
                created_by=instance,
                icon=Icon.objects.get(markup=category[2])
            )

        # Initial configuration
        Configuration.objects.create(user=instance)
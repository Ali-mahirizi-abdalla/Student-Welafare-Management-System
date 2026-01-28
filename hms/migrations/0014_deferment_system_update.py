# Generated manually for deferment system implementation
# Converts LeaveRequest model to DefermentRequest with new fields and statuses

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hms', '0013_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='deferment_type',
            field=models.CharField(
                choices=[
                    ('fee_challenges', 'Fee Challenges'),
                    ('motherhood_fatherhood', 'Motherhood/Fatherhood'),
                    ('gainful_employment', 'Pursuing Gainful Employment'),
                    ('family_disruption', 'Disruption of Family'),
                    ('moving_country', 'Moving Out of the Country'),
                    ('natural_calamity', 'Natural Calamity'),
                    ('political_calamity', 'Political Calamity'),
                    ('program_challenges', 'Challenges in the Current Program'),
                    ('other', 'Others (Please State)'),
                ],
                help_text='Select the reason for deferment',
                max_length=30,
                default='other'
            ),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='other_reason_detail',
            field=models.TextField(blank=True, help_text="If 'Others', please provide details"),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='contact_during_deferment',
            field=models.CharField(blank=True, help_text='Phone number during deferment', max_length=15),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='supporting_documents',
            field=models.FileField(blank=True, help_text='Upload supporting documents if any', null=True, upload_to='deferment_docs/'),
        ),
        
        # Update status choices
        migrations.AlterField(
            model_name='leaverequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Application'),
                    ('under_review', 'Sent for Review'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('resumed', 'Resumed Studies'),
                ],
                default='pending',
                max_length=20
            ),
        ),
        
        # Update model meta
        migrations.AlterModelOptions(
            name='leaverequest',
            options={'ordering': ['-created_at'], 'verbose_name': 'Deferment Request', 'verbose_name_plural': 'Deferment Requests'},
        ),
        
        # Remove old fields last (after new fields are in place)
        migrations.RemoveField(
            model_name='leaverequest',
            name='leave_type',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='contact_during_leave',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='destination',
        ),
    ]

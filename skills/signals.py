from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import VideoTutorial, AudioLesson


@receiver(pre_save, sender=VideoTutorial)
def award_credits_for_video_approval(sender, instance, **kwargs):
    """Award 10 credits when a VideoTutorial is approved"""
    if not instance.pk:
        return  # New object, skip
    try:
        old = VideoTutorial.objects.get(pk=instance.pk)
    except VideoTutorial.DoesNotExist:
        return

    if old.status != 'APPROVED' and instance.status == 'APPROVED':
        instance.approved_at = timezone.now()
        from credits.views import award_credits
        from leaderboard.models import Leaderboard
        from notifications.models import Notification

        award_credits(
            user=instance.user,
            transaction_type='UPLOAD_VIDEO',
            amount=10,
            description=f'Video tutorial approved: {instance.title}',
            related_object_type='VideoTutorial',
            related_object_id=instance.pk,
        )

        # Update leaderboard
        lb, _ = Leaderboard.objects.get_or_create(user=instance.user)
        lb.videos_uploaded += 1
        lb.total_credits_earned += 10
        lb.save()

        # Create notification
        Notification.objects.create(
            user=instance.user,
            notification_type='CREDITS_EARNED',
            title='Your video was approved!',
            message=f'"{instance.title}" has been approved. You earned +10 credits.',
        )


@receiver(pre_save, sender=AudioLesson)
def award_credits_for_audio_approval(sender, instance, **kwargs):
    """Award 5 credits when an AudioLesson is approved"""
    if not instance.pk:
        return
    try:
        old = AudioLesson.objects.get(pk=instance.pk)
    except AudioLesson.DoesNotExist:
        return

    if old.status != 'APPROVED' and instance.status == 'APPROVED':
        instance.approved_at = timezone.now()
        from credits.views import award_credits
        from leaderboard.models import Leaderboard
        from notifications.models import Notification

        award_credits(
            user=instance.user,
            transaction_type='UPLOAD_AUDIO',
            amount=5,
            description=f'Audio lesson approved: {instance.title}',
            related_object_type='AudioLesson',
            related_object_id=instance.pk,
        )

        # Update leaderboard
        lb, _ = Leaderboard.objects.get_or_create(user=instance.user)
        lb.audio_uploaded += 1
        lb.total_credits_earned += 5
        lb.save()

        # Create notification
        Notification.objects.create(
            user=instance.user,
            notification_type='CREDITS_EARNED',
            title='Your audio lesson was approved!',
            message=f'"{instance.title}" has been approved. You earned +5 credits.',
        )

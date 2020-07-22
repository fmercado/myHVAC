
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """should return False if the question date is far ahead in the future"""

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_yesterday(self):
        """should return True if the question is from today o yesterday"""

        time = timezone.now()
        todays_question = Question(pub_date=time)
        self.assertIs(todays_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        """should return False, its and old question > than 1 day"""

        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """It's a recent question, soooo it should yield True"""

        time = timezone.now() - datetime.timedelta(hours=12)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """Create a question with the given text <question_text> and publish in in the future/past
     depending on the sign of days"""

    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTest(TestCase):

    def test_no_questions(self):
        """No questions exists. Yield appropiate message"""

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Questions with pub_date in the past +24hs are published on the index page"""

        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )

    def test_future_question(self):
        """Questions in the future are not displayed"""

        create_question(question_text="John Titor's beloved question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Both past and future question exists, but only past will be shown"""

        create_question(question_text="John Titor's beloved question.", days=30)
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """Test two past questions being displayed at once"""

        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question 2.>', '<Question: Past question 1.>']
                                 )

class QuestionDetailView(TestCase):
    """To test detail view against odd behaviour"""

    def test_future_question(self):
        """Testing detail view against future question. 404 not found should be given"""
        future_question = create_question(question_text="John Titor's Question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """Testing detail view with past question. Question should be rendered."""
        past_question = create_question(question_text="Past Question.", days=-10)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
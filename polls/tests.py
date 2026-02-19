import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Create your tests here.

# helper function
def create_question(question_text, days):
    """
    return Question object with provided text and time offset in days
    (negative for past, positive for future publication date)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_questions(self):
        """
        was_published_recently() should return False for Question with
        pub_date that is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_questions(self):
        """
        was_published_recently() should return False for Question with
        pub_date that is over 1 day old.
        """
        time = timezone.now() - datetime.timedelta(days=1, minutes=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_questions(self):
        """
        was_published_recently() should return True for Question with
        pub_date that is less than 1 day old.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        """
        If no question exist, an appropriate message is displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with past pub_date are displayed on index page
        """
        question = create_question("Past question.", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Questions with future pub_date are not displayed on index page
        """
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Only question with past pub_date are displayed on index page
        """
        question = create_question("Past question.", -30)
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_two_past_questions(self):
        """
        Both questions with past pub_date are displayed on index page in new -> old order
        """
        question1 = create_question("Past question.", -30)
        question2 = create_question("Past question.", -10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question2, question1])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Detail view of question with future pub_date returns 404
        """
        future_question = create_question("Future question.", 5)
        url = reverse("polls:detail", args=(future_question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Detail view of question with past pub_date contains the question's text
        """
        past_question = create_question("Past question.", -5)
        url = reverse("polls:detail", args=(past_question.id, ))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


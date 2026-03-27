import unittest

from registration_form import RegistrationForm
from registration_form_filler import RegistrationFormFiller


class FakeInputElement(object):

    def __init__(self, attrs, xpath):
        self.attrs = attrs
        self.xpath = xpath

    def items(self):
        return self.attrs.items()


class FakeRootTree(object):

    def getpath(self, child):
        return child.xpath


class FakeForm(object):

    def __init__(self, action, children):
        self.action = action
        self.children = children

    def xpath(self, query):
        if query != ".//input":
            raise AssertionError("unexpected xpath query: %s" % query)
        return self.children


class FakeTree(object):

    def __init__(self, form):
        self.form = form

    def getroottree(self):
        return FakeRootTree()


class FakeHtmlParser(object):

    def __init__(self, tree):
        self.tree = tree

    def fromstring(self, html_in):
        self.html_in = html_in
        return self.tree


class FakeFormExtractor(object):

    def __init__(self, form):
        self.form = form

    def extract_forms(self, tree):
        return [(self.form, "registration")]


class RegistrationFormFillerTests(unittest.TestCase):

    def make_filler(self):
        filler = RegistrationFormFiller.__new__(RegistrationFormFiller)
        filler.keywords_dic = {
            "email": ["user[email]", "email"],
            "email_confirmation": ["user[email_confirmation]"],
            "name": ["user[name]"],
            "password": ["user[password]"],
            "password_confirmation": ["user[password_confirmation]"],
        }
        filler.filled_form = RegistrationForm()
        return filler

    def test_init_supports_injected_parser_and_extractor(self):
        input_element = FakeInputElement(
            {"name": "email", "type": "text"},
            "/html/body/form/input[1]",
        )
        form = FakeForm("/register", [input_element])
        tree = FakeTree(form)

        filler = RegistrationFormFiller(
            html_in="<form></form>",
            form_extractor=FakeFormExtractor(form),
            html_parser=FakeHtmlParser(tree),
        )

        self.assertEqual("/register", filler.action)
        self.assertEqual(
            [{"name": "email", "type": "text", "xpath": "/html/body/form/input[1]"}],
            filler.inputs,
        )

    def test_prepare_registration_form_skips_unnamed_inputs_and_normalizes_values(self):
        filler = self.make_filler()
        filler.inputs = [
            {"name": "email", "value": "  user@example.com  "},
            {"name": "empty", "value": "   "},
            {"type": "submit", "value": "go"},
        ]

        prepared = filler.prepare_registration_form()

        self.assertEqual(
            {"email": "user@example.com", "empty": None},
            prepared,
        )

    def test_fill_form_populates_known_field_defaults(self):
        filler = self.make_filler()
        filler.inputs = [
            {"name": "email", "type": "text", "xpath": "//input[@name='email']"},
            {
                "placeholder": "user[password_confirmation]",
                "type": "password",
                "xpath": "//input[@name='password_confirmation']",
            },
        ]

        filled_inputs = filler.fill_form()

        self.assertEqual(
            "blabhalbhalbhalbahlbah@blah.com",
            filled_inputs[0]["value"],
        )
        self.assertEqual(
            "r@nd0mP@ssw0rd",
            filled_inputs[1]["value"],
        )


if __name__ == "__main__":
    unittest.main()

__author__ = 'punk'
import requests
from registration_form import RegistrationForm

class RegistrationFormFiller(object):

    DEFAULT_FIELD_VALUES = {
        "email": "blabhalbhalbhalbahlbah@blah.com",
        "email_confirmation": "blabhalbhalbhalbahlbah@blah.com",
        "name": "Random Name",
        "password": "r@nd0mP@ssw0rd",
        "password_confirmation": "r@nd0mP@ssw0rd",
    }

    def __init__(self, html_in=None, url=None, form_extractor=None,
                 html_parser=None, request_session=None):
        #!needs to take in html
        #words/phrases to check against that indicate that a field
        #is a certain type of field, we'll add to this as we add to
        #forms. This should be checked against field names and placeholders

        self.keywords_dic = {
            "email" : ["user[email]", "email"],
            "email_confirmation" : ["user[email_confirmation]"],
            "name" : ["user[name]"],
            "password" : ["user[password]"],
            "password_confirmation" : ["user[password_confirmation]"],
        }

        self.html_in = html_in
        self.request_session = request_session or requests

        if (form_extractor is None) != (html_parser is None):
            raise ValueError(
                "form_extractor and html_parser must be provided together"
            )

        if self.html_in is None:
            if not url:
                raise ValueError("html_in or url is required")
            try:
                r = self.request_session.get(url, timeout=30)
            except requests.RequestException as exc:
                raise RuntimeError(
                    "failed to fetch registration form HTML from %s" % url
                ) from exc
            self.html_in = r.text

        self.fe = form_extractor or self._load_form_extractor()
        self.html_parser = html_parser or self._load_html_parser()
        self.tree = self.html_parser.fromstring(self.html_in)
        self.form = self._extract_forms_and_types()
        self.action = self.form.action
        self.inputs = self._get_inputs()
        self.filled_inputs = None
        self.filled_form = RegistrationForm()

    def _load_form_extractor(self):

        try:
            from formasaurus import FormExtractor
        except ImportError as exc:
            raise ImportError(
                "formasaurus is required to extract registration forms"
            ) from exc

        return FormExtractor.load()

    def _load_html_parser(self):

        try:
            import lxml.html
        except ImportError as exc:
            raise ImportError(
                "lxml is required to parse registration form HTML"
            ) from exc

        return lxml.html

    def _extract_forms_and_types(self):

        forms = self.fe.extract_forms(self.tree)

        return forms[0][0]

    def _get_inputs(self):

        input_dics = []
        self.some_tree = self.tree.getroottree()
        # Scope input discovery to the extracted form so unrelated page inputs
        # are not copied into the registration payload.
        for child in self.form.xpath(".//input"):
            input_dic = {}
            for k, v in child.items():
                input_dic[k] = v
            #get xpath
            input_xpath = self.some_tree.getpath(child)
            input_dic["xpath"] = input_xpath
            input_dics.append(input_dic)

        return input_dics

    def _normalize_field_value(self, value):

        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None

        return value

    def _detect_input_types(self):

        forms_with_type = []
        for input_attrs in self.inputs:
            if "name" in input_attrs:
                detected_type = self._find_in_keywords_dic(input_attrs["name"])
                input_attrs["detected_type"] = detected_type
                forms_with_type.append(input_attrs)

        #will produce duplicates
        for input_attrs in self.inputs:
            if "detected_type" not in input_attrs and "placeholder" in input_attrs:
                detected_type = self._find_in_keywords_dic(input_attrs["placeholder"])
                input_attrs["detected_type"] = detected_type
                forms_with_type.append(input_attrs)

        self.forms_with_type = forms_with_type

        return forms_with_type

    def _find_in_keywords_dic(self, name_or_placeholder):

        #search through the keywords_dic for name_or_placeholder
        #in the keywords_dic, if it's found in one of the lists
        #of words return the list it was found in (email, email
        # confirmation, etc)
        normalized_value = self._normalize_field_value(name_or_placeholder)
        for k, v in self.keywords_dic.items():
            if normalized_value in v:
                return k
        return None

    def prepare_registration_form(self):

        for input_attrs in self.inputs:
            field_name = input_attrs.get("name")
            if not field_name:
                continue

            if "value" in input_attrs:
                field_value = self._normalize_field_value(input_attrs["value"])
            else:
                field_value = None

            self.filled_form.add_attribute(field_name, field_value)

        return self.filled_form.attribute_dict

    def fill_form(self):

        self._detect_input_types()

        filled_inputs = []
        for input_attrs in self.forms_with_type:
            detected_type = input_attrs.get("detected_type")
            if detected_type in self.DEFAULT_FIELD_VALUES:
                input_attrs["value"] = self.DEFAULT_FIELD_VALUES[detected_type]

            filled_inputs.append(input_attrs)

        return filled_inputs

if __name__ == "__main__":

    import json

    ff = RegistrationFormFiller(url="https://auth.getpebble.com/users/sign_up")
    print(json.dumps(ff.fill_form()))


    #form = extract_forms_and_types("https://auth.getpebble.com/users/sign_up")[0][0]
    #print form.action
    #print get_inputs(form)

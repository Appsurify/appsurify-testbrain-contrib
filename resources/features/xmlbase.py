import itertools
import pathlib
import typing as t
from copy import deepcopy
from testbrain.contrib.report import utils

# try:
#     from lxml import etree
# except ImportError:
#     from xml.etree import ElementTree as etree  # noqa

from xml.etree import ElementTree as etree  # noqa

from testbrain.contrib.report.models.trx import TrxUnitTestResult


class XmlError(Exception):
    """Exception for JUnit XML related errors."""


class Attr(object):
    """An attribute for an XML element.

    By default they are all string values. To support different value types,
    inherit this class and define your own methods.

    Also see: :class:`IntAttr`, :class:`FloatAttr`.
    """

    def __init__(self, name: str = None):
        self.name = name

    def __get__(self, instance, cls):
        """Get value from attribute, return ``None`` if attribute doesn't exist."""
        return instance.elem.attrib.get(self.name)

    def __set__(self, instance, value: t.Union[str, int, float]):
        """Sets XML element attribute."""
        if value is not None:
            instance.elem.attrib[self.name] = str(value)


class IntAttr(Attr):
    """An integer attribute for an XML element.

    This class is used internally for counting testcases, but you could use
    it for any specific purpose.
    """

    def __get__(self, instance, cls):
        result = super().__get__(instance, cls)
        if result is None and isinstance(instance, (JUnitXml, TestSuite)):
            instance.update_statistics()
            result = super().__get__(instance, cls)
        return int(result) if result else None

    def __set__(self, instance, value: int):
        if not isinstance(value, int):
            raise TypeError("Expected integer value.")
        super().__set__(instance, value)


class FloatAttr(Attr):
    """A float attribute for an XML element.

    This class is used internally for counting test durations, but you could
    use it for any specific purpose.
    """

    def __get__(self, instance, cls):
        result = super().__get__(instance, cls)
        if result is None and isinstance(instance, (JUnitXml, TestSuite)):
            instance.update_statistics()
            result = super().__get__(instance, cls)
        return float(result.replace(",", "")) if result else None

    def __set__(self, instance, value: float):
        if not (isinstance(value, float) or isinstance(value, int)):
            raise TypeError("Expected float value.")
        super().__set__(instance, value)


def attributed(cls):
    """Decorator to read XML element attribute name from class attribute."""
    for key, value in vars(cls).items():
        if isinstance(value, Attr):
            if not value.name:
                value.name = key
    return cls


class XMLMeta(type):
    """Metaclass to decorate the XML class."""

    def __new__(meta, name, bases, methods):
        cls = super(XMLMeta, meta).__new__(meta, name, bases, methods)
        cls = attributed(cls)
        return cls


class Element(metaclass=XMLMeta):
    """Base class for all JUnit XML elements."""

    _namespace: str
    _tag: str
    _elem: etree.Element

    def __init__(self, name: str = None, namespace: str = None):
        if not name:
            name = self._tag

        if not namespace:
            self._namespace = ""

        self._elem = etree.Element(f"{self._namespace}{name}")

    def __hash__(self):
        return hash(etree.tostring(self._elem))

    def __repr__(self):
        tag = self._elem.tag
        keys = sorted(self._elem.attrib.keys())
        if keys:
            attrs_str = " ".join(
                '%s="%s"' % (key, self._elem.attrib[key]) for key in keys
            )
            return """<Element '%s' %s>""" % (tag, attrs_str)

        return """<Element '%s'>""" % tag

    def append(self, sub_elem):
        """Add the element subelement to the end of this elements internal
        list of subelements.
        """
        self._elem.append(sub_elem._elem)

    def extend(self, sub_elems):
        """Add elements subelement to the end of this elements internal
        list of subelements.
        """
        self._elem.extend((sub_elem._elem for sub_elem in sub_elems))

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        self._tag = tag

    @property
    def elem(self):
        return self._elem

    @elem.setter
    def elem(self, elem):
        self._namespace = utils.get_namespace(self._elem)
        self._elem = elem
        print("SETTED _ELEM")

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    @classmethod
    def fromstring(cls, text: t.AnyStr):
        """Construct JUnit object *cls* from XML string *test*."""
        text = utils.normalize_xml_text(text)

        instance = cls()
        instance._elem = etree.fromstring(text)  # nosec
        instance._namespace = utils.get_namespace(instance._elem)
        return instance

    @classmethod
    def from_elem(cls, elem):
        """Construct JUnit objects from an ElementTree element *elem*."""
        if elem is None:
            return
        instance = cls()
        if isinstance(elem, Element):
            instance._elem = elem._elem
        else:
            instance._elem = elem
        instance._namespace = utils.get_namespace(instance._elem)
        return instance

    def iter_children(self, child_elem):
        """Iterate through specified *child_elem* type elements."""
        e = self._elem.findall(f"{self._namespace}{child_elem._tag}")

        elems = self._elem.iterfind(f"{self._namespace}{child_elem._tag}")
        for elem in elems:
            yield child_elem.from_elem(elem)

    def child(self, child_elem):
        """Find a single child of specified *child_elem* type."""
        elem = self._elem.find(f"{self._namespace}{child_elem._tag}")
        return child_elem.from_elem(elem)

    def remove(self, sub_elem):
        """Remove sub_element *sub_elem*."""
        for elem in self._elem.iterfind(sub_elem._tag):
            child = sub_elem.__class__.from_elem(elem)
            if child == sub_elem:
                self._elem.remove(child._elem)

    def tostring(self):
        """Convert element to XML string."""
        return etree.tostring(self._elem, encoding="utf-8")


# ------------- JUNIT XML
class Result(Element):
    """Base class for test result.

    Attributes:
        message: Result as message string.
        type: Message type.
    """

    _tag = None
    message = Attr()
    type = Attr()

    def __init__(self, message: str = None, type_: str = None):
        super(Result, self).__init__(self._tag)
        if message:
            self.message = message
        if type_:
            self.type = type_

    def __eq__(self, other):
        return (
            self.tag == other.tag
            and self.type == other.type
            and self.message == other.message
        )

    @property
    def text(self):
        return self._elem.text

    @text.setter
    def text(self, value: str):
        self._elem.text = value


class Skipped(Result):
    """Test result when the case is skipped."""

    _tag = "skipped"

    def __eq__(self, other):
        return super().__eq__(other)


class Failure(Result):
    """Test result when the case failed."""

    _tag = "failure"

    def __eq__(self, other):
        return super().__eq__(other)


class Error(Result):
    """Test result when the case has errors during execution."""

    _tag = "error"

    def __eq__(self, other):
        return super().__eq__(other)


POSSIBLE_RESULTS = {Failure, Error, Skipped}


class System(Element):
    """Parent class for :class:`SystemOut` and :class:`SystemErr`.

    Attributes:
        text: The output message.
    """

    _tag = ""

    def __init__(self, content: str = None):
        super().__init__(self._tag)
        self.text = content

    @property
    def text(self):
        return self._elem.text

    @text.setter
    def text(self, value: str):
        self._elem.text = value


class SystemOut(System):
    _tag = "system-out"


class SystemErr(System):
    _tag = "system-err"


class TestCase(Element):
    """Object to store a testcase and its result.

    Attributes:
        name: Name of the testcase.
        classname: The parent class of the testcase.
        time: The time consumed by the testcase.
    """

    _tag = "testcase"
    name = Attr()
    classname = Attr()
    time = FloatAttr()

    def __init__(self, name: str = None, classname: str = None, time: float = None):
        super().__init__(self._tag)
        if name is not None:
            self.name = name
        if classname is not None:
            self.classname = classname
        if time is not None:
            self.time = float(time)

    def __hash__(self):
        return super().__hash__()

    def __iter__(self):
        all_types = set.union(POSSIBLE_RESULTS, {SystemOut}, {SystemErr})
        for elem in self._elem.iter():
            for entry_type in all_types:
                if elem.tag == entry_type._tag:
                    yield entry_type.from_elem(elem)

    def __eq__(self, other):
        # TODO: May not work correctly if unreliable hash method is used.
        return hash(self) == hash(other)

    @property
    def is_passed(self):
        """Whether this testcase was a success (i.e. if it isn't skipped, failed,
        or errored)."""
        return not self.result

    @property
    def is_skipped(self):
        """Whether this testcase was skipped."""
        for r in self.result:
            if isinstance(r, Skipped):
                return True
        return False

    @property
    def result(self):
        """A list of :class:`Failure`, :class:`Skipped`, or :class:`Error` objects."""
        results = []
        for entry in self:
            if isinstance(entry, tuple(POSSIBLE_RESULTS)):
                results.append(entry)

        return results

    @result.setter
    def result(self, value: Result):
        # First remove all existing results
        for entry in self.result:
            if any(isinstance(entry, r) for r in POSSIBLE_RESULTS):
                self.remove(entry)

        for entry in value:
            if any(isinstance(entry, r) for r in POSSIBLE_RESULTS):
                self.append(entry)

    @property
    def system_out(self):
        """stdout."""
        elem = self.child(SystemOut)
        if elem is not None:
            return elem.text
        return None

    @system_out.setter
    def system_out(self, value: str):
        out = self.child(SystemOut)
        if out is not None:
            out.text = value
        else:
            out = SystemOut(value)
            self.append(out)

    @property
    def system_err(self):
        """stderr."""
        elem = self.child(SystemErr)
        if elem is not None:
            return elem.text
        return None

    @system_err.setter
    def system_err(self, value: str):
        err = self.child(SystemErr)
        if err is not None:
            err.text = value
        else:
            err = SystemErr(value)
            self.append(err)


class Property(Element):
    """A key/value pare that's stored in the testsuite.

    Use it to store anything you find interesting or useful.

    Attributes:
        name: The property name.
        value: The property value.
    """

    _tag = "property"
    name = Attr()
    value = Attr()

    def __init__(self, name: str = None, value: str = None):
        super().__init__(self._tag)
        self.name = name
        self.value = value

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        """Supports sort() for properties."""
        return self.name > other.name


class Properties(Element):
    """A list of properties inside a testsuite.

    See :class:`Property`
    """

    _tag = "properties"

    def __init__(self):
        super().__init__(self._tag)

    def add_property(self, property_: Property):
        self.append(property_)

    def __iter__(self):
        return super().iter_children(Property)

    def __eq__(self, other):
        p1 = list(self)
        p2 = list(other)
        p1.sort()
        p2.sort()
        if len(p1) != len(p2):
            return False
        for e1, e2 in zip(p1, p2):
            if e1 != e2:
                return False
        return True


class TestSuite(Element):
    """The <testsuite> object.

    Attributes:
        name: The name of the testsuite.
        hostname: Name of the test machine.
        time: Time consumed by the testsuite.
        timestamp: When the test was run.
        tests: Total number of tests.
        failures: Number of failed tests.
        errors: Number of cases with errors.
        skipped: Number of skipped cases.
    """

    _tag = "testsuite"
    name = Attr()
    hostname = Attr()
    time = FloatAttr()
    timestamp = Attr()
    tests = IntAttr()
    failures = IntAttr()
    errors = IntAttr()
    skipped = IntAttr()

    def __init__(self, name=None):
        super().__init__(self._tag)
        self.name = name
        self.filepath = None

    def __iter__(self):
        return itertools.chain(
            super().iter_children(TestCase),
            (case for suite in super().iter_children(TestSuite) for case in suite),
        )

    def __len__(self):
        return len(list(self.__iter__()))

    def __eq__(self, other):
        def props_eq(props1, props2):
            props1 = list(props1)
            props2 = list(props2)
            if len(props1) != len(props2):
                return False
            props1.sort(key=lambda x: x.name)
            props2.sort(key=lambda x: x.name)
            zipped = zip(props1, props2)
            return all(x == y for x, y in zipped)

        return (
            self.name == other.name
            and self.hostname == other.hostname
            and self.timestamp == other.timestamp
        ) and props_eq(self.properties(), other.properties())

    def __add__(self, other):
        if self == other:
            # Merge the two testsuites
            result = deepcopy(self)
            for case in other:
                result.add_testcase_no_update_stats(case)
            for suite in other.testsuites():
                result.add_testsuite(suite)
            result.update_statistics()
        else:
            # Create a new test result containing two testsuites
            result = JUnitXml()
            result.add_testsuite(self)
            result.add_testsuite(other)
        return result

    def __iadd__(self, other):
        if self == other:
            for case in other:
                self.add_testcase_no_update_stats(case)
            for suite in other.testsuites():
                self.add_testsuite(suite)
            self.update_statistics()
            return self

        result = JUnitXml()
        result.filepath = self.filepath
        result.add_testsuite(self)
        result.add_testsuite(other)
        return result

    def remove_testcase(self, testcase):
        """Remove testcase *testcase* from the testsuite."""
        for case in self:
            if case == testcase:
                super().remove(case)
                self.update_statistics()

    def update_statistics(self):
        """Update test count and test time."""
        tests = errors = failures = skipped = 0
        time = 0
        for case in self:
            tests += 1
            if case.time is not None:
                time += case.time
            for entry in case.result:
                if isinstance(entry, Failure):
                    failures += 1
                elif isinstance(entry, Error):
                    errors += 1
                elif isinstance(entry, Skipped):
                    skipped += 1
        self.tests = tests
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.time = round(time, 3)

    def add_property(self, name, value):
        """Add a property *name* = *value* to the testsuite.

        See :class:`Property` and :class:`Properties`.
        """

        props = self.child(Properties)
        if props is None:
            props = Properties()
            self.append(props)
        prop = Property(name, value)
        props.add_property(prop)

    def add_testcase(self, testcase):
        """Add a testcase *testcase* to the testsuite."""
        self.append(testcase)
        self.update_statistics()

    def add_testcases(self, testcases):
        """Add testcases *testcases* to the testsuite."""
        self.extend(testcases)
        self.update_statistics()

    def add_testcase_no_update_stats(self, testcase):
        """Add *testcase* to the testsuite (without updating statistics).

        For internal use only to avoid quadratic behaviour in merge.
        """
        self.append(testcase)

    def add_testsuite(self, suite):
        """Add a testsuite *suite* to the testsuite."""
        self.append(suite)

    def properties(self):
        """Iterate through all :class:`Property` elements in the testsuite."""
        props = self.child(Properties)
        if props is None:
            return
        for prop in props:
            yield prop

    def remove_property(self, property_: Property):
        """Remove property *property_* from the testsuite."""
        props = self.child(Properties)
        if props is None:
            return
        for prop in props:
            if prop == property_:
                props.remove(property_)

    def testsuites(self):
        """Iterate through all testsuites."""
        for suite in self.iter_children(TestSuite):
            yield suite


class JUnitXml(Element):
    """The JUnitXml root object.

    It may contain ``<TestSuites>`` or a ``<TestSuite>``.

    Attributes:
        name: Name of the testsuite if it only contains one testsuite.
        time: Time consumed by the testsuites.
        tests: Total number of tests.
        failures: Number of failed cases.
        errors: Number of cases with errors.
        skipped: Number of skipped cases.
    """

    _tag = "testsuites"
    name = Attr()
    time = FloatAttr()
    tests = IntAttr()
    failures = IntAttr()
    errors = IntAttr()
    skipped = IntAttr()

    def __init__(self, name=None):
        super().__init__(self._tag)
        self.filepath = None
        self.name = name

    def __iter__(self):
        return super().iter_children(TestSuite)

    def __len__(self):
        return len(list(self.__iter__()))

    def __add__(self, other):
        result = JUnitXml()
        for suite in self:
            result.add_testsuite(suite)
        for suite in other:
            result.add_testsuite(suite)
        return result

    def __iadd__(self, other):
        if other.elem.tag == "testsuites":
            for suite in other:
                self.add_testsuite(suite)
        elif other.elem.tag == "testsuite":
            suite = TestSuite(name=other.name)
            for case in other:
                suite.add_testcase_no_update_stats(case)
            self.add_testsuite(suite)
            self.update_statistics()

        return self

    def add_testsuite(self, suite: TestSuite):
        """Add a testsuite."""
        for existing_suite in self:
            if existing_suite == suite:
                for case in suite:
                    existing_suite.add_testcase_no_update_stats(case)
                return
        self.append(suite)

    def update_statistics(self):
        """Update test count, time, etc."""
        time = 0
        tests = failures = errors = skipped = 0
        for suite in self:
            suite.update_statistics()
            tests += suite.tests
            failures += suite.failures
            errors += suite.errors
            skipped += suite.skipped
            time += suite.time
        self.tests = tests
        self.failures = failures
        self.errors = errors
        self.skipped = skipped
        self.time = round(time, 3)

    @classmethod
    def from_root(cls, root_elem: Element):
        """Construct JUnit objects from an elementTree root element."""
        if root_elem.tag == "testsuites":
            instance = cls()
        elif root_elem.tag == "testsuite":
            # testsuite_elem = deepcopy(root_elem)
            # root_elem = cls()
            # root_elem.add_testsuite(testsuite_elem)
            instance = TestSuite()
        else:
            raise XmlError("Invalid format.")
        instance._elem = root_elem
        return instance

    @classmethod
    def fromstring(cls, text: t.AnyStr):
        """Construct JUnit objects from an XML string."""
        text = utils.normalize_xml_text(text)
        root_elem = etree.fromstring(text)  # nosec
        return cls.from_root(root_elem)

    @classmethod
    def fromfile(cls, filepath: pathlib.Path, parse_func=None):
        """Initiate the object from a report file."""
        if parse_func:
            tree = parse_func(filepath)
        else:
            tree = etree.parse(filepath)  # nosec
        root_elem = tree.getroot()
        instance = cls.from_root(root_elem)
        instance.filepath = filepath
        return instance


# -------- TRX


class TrxInnerResults(Element):
    _tag = "InnerResults"


class TrxUnitTestResult(Element):
    _tag = "UnitTestResult"

    execution_id = Attr("executionId")
    test_id = Attr("testId")
    test_name = Attr("testName")
    computer_name = Attr("computerName")
    duration = Attr("duration")
    start_time = Attr("startTime")
    end_time = Attr("endTime")
    test_type = Attr("testType")
    outcome = Attr("outcome")
    test_list_id = Attr("testListId")
    relative_results_directory = Attr("relativeResultsDirectory")


class TrxResults(Element):
    _tag = "Results"

    def unit_test_results(self):
        unit_test_results = self.iter_children(TrxUnitTestResult)
        return unit_test_results


class TrxTestDefinition(Element):
    ...


class TrxExecution(Element):
    _tag = "Execution"

    id = Attr()


class TrxTestMethod(Element):
    _tag = "TestMethod"

    name = Attr()
    classname = Attr("className")
    codebase = Attr("codeBase")
    adapter_type_name = Attr("adapterTypeName")


class TrxUnitTest(TrxTestDefinition):
    _tag = "UnitTest"

    id = Attr()
    name = Attr()
    storage = Attr()

    @property
    def execution(self):
        execution = self.child(TrxExecution)
        return execution

    @property
    def test_method(self):
        test_method = self.child(TrxTestMethod)
        return test_method


class TrxTestDefinitions(Element):
    _tag = "TestDefinitions"

    def unit_tests(self):
        unit_tests = self.iter_children(TrxUnitTest)
        return unit_tests


class TrxCounters(Element):
    _tag = "Counters"

    total = IntAttr("total")
    expected = IntAttr("executed")
    passed = IntAttr("passed")
    failed = IntAttr("failed")
    errors = IntAttr("error")


class TrxResultSummary(Element):
    _tag = "ResultSummary"

    outcome = Attr("outcome")
    # TODO: Output first or StdOut

    def counters(self):
        counters = self.child(TrxCounters)
        return counters


class TrxTimes(Element):
    _tag = "Times"
    creation = Attr()
    queuing = Attr()
    start = Attr()
    finish = Attr()

    def __init__(self, name=None):
        super().__init__(self._tag)
        self.name = name
        self.filepath = None


class TrxXML(Element):
    _tag = "TestRun"
    id = Attr()
    name = Attr()
    run_user = Attr(name="runUser")

    def __init__(self, name=None):
        super().__init__(self._tag)
        self.filepath = None
        self.name = name

    def times(self):
        times = self.child(TrxTimes)
        return times

    def result_summary(self):
        result_summary = self.child(TrxResultSummary)
        return result_summary

    def test_definitions(self):
        test_definitions = self.child(TrxTestDefinitions)
        return test_definitions

    def results(self):
        results = self.child(TrxResults)
        return results

    @classmethod
    def from_root(cls, root_elem: Element):
        """Construct JUnit objects from an elementTree root element."""
        root_namespace = utils.get_namespace(root_elem)
        if root_elem.tag == f"{root_namespace}TestRun":
            instance = cls()
        else:
            raise XmlError("Invalid format.")

        instance._namespace = root_namespace
        instance._elem = root_elem

        return instance

    @classmethod
    def fromstring(cls, text: t.AnyStr):
        """Construct JUnit objects from an XML string."""
        text = utils.normalize_xml_text(text)
        root_elem = etree.fromstring(text)  # nosec
        return cls.from_root(root_elem)

    @classmethod
    def fromfile(cls, filepath: pathlib.Path, parse_func=None):
        """Initiate the object from a report file."""
        if parse_func:
            tree = parse_func(filepath)
        else:
            tree = etree.parse(filepath)  # nosec
        root_elem = tree.getroot()
        instance = cls.from_root(root_elem)
        instance.filepath = filepath
        return instance

"""Type definitions for the ClassCharts API."""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


class ClassChartsResponse(TypedDict, total=False):
    """Base response type from ClassCharts API.
    
    Contains common fields. Subclasses add data and meta fields with specific types.
    """

    error: Optional[str]
    success: int


# Student types
class Student(TypedDict, total=False):
    """Student information."""

    id: int
    name: str
    first_name: str
    last_name: str
    avatar_url: str
    display_behaviour: bool
    display_parent_behaviour: bool
    display_homework: bool
    display_rewards: bool
    display_detentions: bool
    display_report_cards: bool
    display_classes: bool
    display_announcements: bool
    display_attendance: bool
    display_attendance_type: str
    display_attendance_percentage: bool
    display_activity: bool
    display_mental_health: bool
    display_timetable: bool
    is_disabled: bool
    display_two_way_communications: bool
    display_absences: bool
    can_upload_attachments: Optional[bool]
    display_event_badges: bool
    display_avatars: bool
    display_concern_submission: bool
    display_custom_fields: bool
    pupil_concerns_help_text: str
    allow_pupils_add_timetable_notes: bool
    announcements_count: int
    messages_count: int
    pusher_channel_name: str
    has_birthday: bool
    has_new_survey: bool
    survey_id: Optional[int]
    detention_alias_plural_uc: str


class GetStudentInfoData(TypedDict):
    """Data for get student info response."""

    user: Student


class GetStudentInfoMeta(TypedDict):
    """Meta for get student info response."""

    version: str


class GetStudentInfoResponse(ClassChartsResponse):
    """Response for get student info."""

    data: GetStudentInfoData
    meta: GetStudentInfoMeta


# Behaviour types
class GetBehaviourOptions(TypedDict, total=False):
    """Options for getting behaviour data."""

    from_date: str  # YYYY-MM-DD format
    to_date: str  # YYYY-MM-DD format


class BehaviourTimelinePoint(TypedDict):
    """A point in the behaviour timeline."""

    positive: int
    negative: int
    name: str
    start: str
    end: str


class BehaviourResponseData(TypedDict):
    """Data for behaviour response."""

    timeline: List[BehaviourTimelinePoint]
    positive_reasons: Dict[str, int]
    negative_reasons: Dict[str, int]
    other_positive: List[str]
    other_negative: List[str]
    other_positive_count: List[Dict[str, int]]
    other_negative_count: List[Dict[str, int]]


class BehaviourResponseMeta(TypedDict):
    """Meta for behaviour response."""

    start_date: str
    end_date: str
    step_size: str


class BehaviourResponse(ClassChartsResponse):
    """Response for behaviour data."""

    data: BehaviourResponseData
    meta: BehaviourResponseMeta


# Activity types
class GetActivityOptions(TypedDict, total=False):
    """Options for getting activity data."""

    from_date: str  # YYYY-MM-DD format
    to_date: str  # YYYY-MM-DD format
    last_id: str  # ID of the last activity point (used in pagination)


class GetFullActivityOptions(TypedDict):
    """Options for getting full activity data."""

    from_date: str  # YYYY-MM-DD format
    to_date: str  # YYYY-MM-DD format


class ActivityPoint(TypedDict, total=False):
    """An activity point."""

    id: int
    type: Literal["detention", "notice", "attendance_event", "question", "event", "behaviour"]
    polarity: Optional[Literal["positive", "blank", "negative"]]
    reason: str
    score: int
    timestamp: str
    timestamp_custom_time: Optional[str]
    style: Dict[
        str,
        Optional[
            Union[
                str,
                Literal[
                    "notice-color", "colour-orange", "colour-blue", "colour-purple", "colour-green"
                ],
            ]
        ],
    ]
    pupil_name: str
    lesson_name: Optional[str]
    teacher_name: Optional[str]
    room_name: Optional[str]
    note: Optional[str]
    _can_delete: bool
    badges: str
    detention_date: Optional[str]
    detention_time: Optional[str]
    detention_location: Optional[str]
    detention_type: Optional[str]


class ActivityResponseMeta(TypedDict):
    """Meta for activity response."""

    start_date: str
    end_date: str
    last_id: Union[int, bool]
    step_size: str
    detention_alias_uc: str


class ActivityResponse(ClassChartsResponse):
    """Response for activity data."""

    data: List[ActivityPoint]
    meta: ActivityResponseMeta


# Homework types
DisplayDate = Literal["due_date", "issue_date"]


class GetHomeworkOptions(TypedDict, total=False):
    """Options for getting homework data."""

    display_date: DisplayDate  # Default: "issue_date"
    from_date: str  # YYYY-MM-DD format
    to_date: str  # YYYY-MM-DD format


class TeacherValidatedHomeworkAttachment(TypedDict):
    """Teacher validated homework attachment."""

    id: int
    file_name: str
    file: str
    validated_file: str


class TeacherValidatedHomeworkLink(TypedDict):
    """Teacher validated homework link."""

    link: str
    validated_link: str


class StudentHomeworkAttachment(TypedDict):
    """Student homework attachment."""

    id: int
    file_name: str
    file: str
    validated_file: str
    teacher_note: str
    teacher_homework_attachments: List[TeacherValidatedHomeworkAttachment]
    can_delete: bool


class HomeworkStatus(TypedDict, total=False):
    """Homework status."""

    id: int
    state: Optional[Literal["not_completed", "late", "completed"]]
    mark: Optional[str]
    mark_relative: int
    ticked: Literal["yes", "no"]
    allow_attachments: bool
    allow_marking_completed: bool
    first_seen_date: Optional[str]
    last_seen_date: Optional[str]
    attachments: List[StudentHomeworkAttachment]
    has_feedback: bool


class Homework(TypedDict):
    """Homework information."""

    lesson: str
    subject: str
    teacher: str
    homework_type: str
    id: int
    title: str
    meta_title: str
    description: str
    issue_date: str
    due_date: str
    completion_time_unit: str
    completion_time_value: str
    publish_time: str
    status: HomeworkStatus
    validated_links: List[TeacherValidatedHomeworkLink]
    validated_attachments: List[TeacherValidatedHomeworkAttachment]


class HomeworksResponseMeta(TypedDict):
    """Meta for homeworks response."""

    start_date: str
    end_date: str
    display_type: DisplayDate
    max_files_allowed: int
    allowed_file_types: List[str]
    this_week_due_count: int
    this_week_outstanding_count: int
    this_week_completed_count: int
    allow_attachments: bool
    display_marks: bool


class HomeworksResponse(ClassChartsResponse):
    """Response for homeworks data."""

    data: List[Homework]
    meta: HomeworksResponseMeta


# Lessons types
class GetLessonsOptions(TypedDict):
    """Options for getting lessons data."""

    date: str  # YYYY-MM-DD format


class Lesson(TypedDict, total=False):
    """Lesson information."""

    teacher_name: str
    teacher_id: str
    lesson_name: str
    subject_name: str
    is_alternative_lesson: bool
    is_break: bool
    period_name: str
    period_number: str
    room_name: str
    date: str
    start_time: str
    end_time: str
    key: int
    note_abstract: str
    note: str
    pupil_note_abstract: str
    pupil_note: str
    pupil_note_raw: str


class PeriodMeta(TypedDict):
    """Period metadata."""

    number: str
    start_time: str
    end_time: str


class LessonsResponseMeta(TypedDict):
    """Meta for lessons response."""

    dates: List[str]
    timetable_dates: List[str]
    periods: List[PeriodMeta]
    start_time: str
    end_time: str


class LessonsResponse(ClassChartsResponse):
    """Response for lessons data."""

    data: List[Lesson]
    meta: LessonsResponseMeta


# Badges types
class LessonPupilBehaviour(TypedDict):
    """Lesson pupil behaviour."""

    reason: str
    score: int
    icon: str
    polarity: str
    timestamp: str
    teacher: Dict[str, str]  # title, first_name, last_name


class PupilEvent(TypedDict):
    """Pupil event."""

    timestamp: str
    lesson_pupil_behaviour: LessonPupilBehaviour
    event: Dict[str, str]  # label


class Badge(TypedDict):
    """Badge information."""

    id: int
    name: str
    icon: str
    colour: str
    created_date: str
    pupil_badges: List[Dict[str, PupilEvent]]  # pupil_event
    icon_url: str


class BadgesResponse(ClassChartsResponse):
    """Response for badges data."""

    data: List[Badge]
    meta: List  # Empty list


# Detentions types
class DetentionPupil(TypedDict):
    """Detention pupil information."""

    id: int
    first_name: str
    last_name: str
    school: Dict[str, Literal["yes", "no"]]  # opt_notes_names, opt_notes_comments, etc.


class DetentionLesson(TypedDict, total=False):
    """Detention lesson information."""

    id: int
    name: str
    subject: Optional[Dict[str, Union[int, str]]]  # id, name


class DetentionLessonPupilBehaviour(TypedDict):
    """Detention lesson pupil behaviour."""

    reason: str


class DetentionTeacher(TypedDict, total=False):
    """Detention teacher information."""

    id: int
    first_name: str
    last_name: str
    title: str


class DetentionType(TypedDict, total=False):
    """Detention type."""

    name: str


class Detention(TypedDict, total=False):
    """Detention information."""

    id: int
    attended: Literal["yes", "no", "upscaled", "pending"]
    date: Optional[str]
    length: Optional[int]
    location: Optional[str]
    notes: Optional[str]
    time: Optional[str]
    pupil: DetentionPupil
    lesson: Optional[DetentionLesson]
    lesson_pupil_behaviour: DetentionLessonPupilBehaviour
    teacher: Optional[DetentionTeacher]
    detention_type: Optional[DetentionType]


class DetentionsMeta(TypedDict):
    """Meta for detentions response."""

    detention_alias_plural: str


class DetentionsResponse(ClassChartsResponse):
    """Response for detentions data."""

    data: List[Detention]
    meta: DetentionsMeta


# Announcements types
class AnnouncementConsent(TypedDict, total=False):
    """Announcement consent."""

    consent_given: Literal["yes", "no"]
    comment: Optional[str]
    parent_name: str


class AnnouncementPupilConsent(TypedDict, total=False):
    """Announcement pupil consent."""

    pupil: Dict[str, str]  # id, first_name, last_name
    can_change_consent: bool
    consent: Optional[AnnouncementConsent]


class Announcement(TypedDict, total=False):
    """Announcement information."""

    id: int
    title: str
    description: Optional[str]
    school_name: str
    teacher_name: str
    school_logo: Optional[str]
    sticky: Literal["yes", "no"]
    state: Optional[str]
    timestamp: str
    attachments: List[Dict[str, str]]  # filename, url
    for_pupils: List[str]
    comment_visibility: str
    allow_comments: Literal["yes", "no"]
    allow_reactions: Literal["yes", "no"]
    allow_consent: Literal["yes", "no"]
    priority_pinned: Literal["yes", "no"]
    requires_consent: Literal["yes", "no"]
    can_change_consent: bool
    consent: Optional[AnnouncementConsent]
    pupil_consents: List[AnnouncementPupilConsent]


class AnnouncementsResponse(ClassChartsResponse):
    """Response for announcements data."""

    data: List[Announcement]
    meta: List  # Empty list


# Pupil types (for parent client)
class Pupil(Student, total=False):
    """Pupil information (extends Student with additional fields)."""

    school_name: str
    school_logo: str
    timezone: str
    display_covid_tests: bool
    can_record_covid_tests: bool
    detention_yes_count: int
    detention_no_count: int
    detention_pending_count: int
    detention_upscaled_count: int
    homework_todo_count: int
    homework_late_count: int
    homework_not_completed_count: int
    homework_excused_count: int
    homework_completed_count: int
    homework_submitted_count: int


GetPupilsResponse = List[Pupil]


# Attendance types
class GetAttendanceOptions(TypedDict):
    """Options for getting attendance data."""

    from_date: str  # YYYY-MM-DD format
    to_date: str  # YYYY-MM-DD format


class AttendancePeriod(TypedDict, total=False):
    """Attendance period information."""

    code: str
    status: Literal["yes", "present", "ignore", "no", "absent", "excused", "late"]
    late_minutes: Union[int, str]
    lesson_name: str
    room_name: str


class AttendanceMeta(TypedDict):
    """Meta for attendance response."""

    dates: List[str]
    sessions: List[str]
    start_date: str
    end_date: str
    percentage: str
    percentage_singe_august: str


AttendanceData = Dict[str, Dict[str, AttendancePeriod]]


class AttendanceResponse(ClassChartsResponse):
    """Response for attendance data."""

    data: AttendanceData
    meta: AttendanceMeta


# Rewards types
class Reward(TypedDict):
    """Reward information."""

    id: int
    name: str
    description: str
    photo: str
    price: int
    stock_control: bool
    stock: int
    can_purchase: bool
    unable_to_purchase_reason: str
    once_per_pupil: bool
    purchased: bool
    purchased_count: Union[str, int]
    price_balance_difference: int


class RewardsMeta(TypedDict):
    """Meta for rewards response."""

    pupil_score_balance: int


class RewardsResponse(ClassChartsResponse):
    """Response for rewards data."""

    data: List[Reward]
    meta: RewardsMeta


class RewardPurchaseData(TypedDict):
    """Reward purchase data."""

    single_purchase: Literal["yes", "no"]
    order_id: int
    balance: int


class RewardPurchaseResponse(ClassChartsResponse):
    """Response for reward purchase."""

    data: RewardPurchaseData
    meta: List  # Empty list


# Pupil fields types
class PupilField(TypedDict):
    """Pupil field information."""

    id: int
    name: str
    graphic: str
    value: str


class PupilFieldsData(TypedDict):
    """Pupil fields data."""

    note: str
    fields: List[PupilField]


class PupilFieldsResponse(ClassChartsResponse):
    """Response for pupil fields data."""

    data: PupilFieldsData
    meta: List  # Empty list


# Password change
class ChangePasswordResponse(ClassChartsResponse):
    """Response for password change."""

    data: List
    meta: List


# Student code types
class GetStudentCodeOptions(TypedDict):
    """Options for getting student code."""

    date_of_birth: str  # YYYY-MM-DD format


class GetStudentCodeResponseData(TypedDict):
    """Data for get student code response."""

    code: str


class GetStudentCodeResponse(ClassChartsResponse):
    """Response for get student code."""

    data: GetStudentCodeResponseData
    meta: List  # Empty list

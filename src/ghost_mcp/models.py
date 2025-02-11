"""Data models for Ghost MCP server."""

from typing import TypedDict, List, Optional

class Post(TypedDict):
    """Ghost blog post data model."""
    id: str
    title: str
    status: str
    url: str
    created_at: str
    html: Optional[str]
    plaintext: Optional[str]
    excerpt: Optional[str]

class User(TypedDict):
    """Ghost user data model."""
    id: str
    name: str
    email: str
    slug: str
    status: str
    location: Optional[str]
    website: Optional[str]
    bio: Optional[str]
    profile_image: Optional[str]
    cover_image: Optional[str]
    created_at: str
    last_seen: Optional[str]
    roles: List[dict]

class Member(TypedDict):
    """Ghost member data model."""
    id: str
    name: str
    email: str
    status: str
    created_at: str
    note: Optional[str]
    labels: List[dict]
    email_count: int
    email_opened_count: int
    email_open_rate: float
    last_seen_at: Optional[str]
    newsletters: List[dict]
    subscriptions: List[dict]

class Tier(TypedDict):
    """Ghost tier data model."""
    id: str
    name: str
    description: Optional[str]
    type: str
    active: bool
    welcome_page_url: Optional[str]
    created_at: str
    updated_at: str
    monthly_price: Optional[dict]
    yearly_price: Optional[dict]
    currency: str
    benefits: List[str]

class Offer(TypedDict):
    """Ghost offer data model."""
    id: str
    name: str
    code: str
    display_title: str
    display_description: Optional[str]
    type: str
    status: str
    cadence: str
    amount: float
    duration: str
    currency: str
    tier: dict
    redemption_count: int
    created_at: str

class Newsletter(TypedDict):
    """Ghost newsletter data model."""
    id: str
    name: str
    description: Optional[str]
    status: str
    visibility: str
    subscribe_on_signup: bool
    sort_order: int
    sender_name: str
    sender_email: Optional[str]
    sender_reply_to: Optional[str]
    show_header_icon: bool
    show_header_title: bool
    show_header_name: bool
    show_feature_image: bool
    title_font_category: str
    body_font_category: str
    show_badge: bool
    created_at: str
    updated_at: str

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ContractType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERN = "intern"


class ExperienceLevel(str, Enum):
    JUNIOR = "Junior"
    MID_LEVEL = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    EXECUTIVE = "Executive"
    UNKNOWN = "Unknown"


class JobLocationType(str, Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    IN_PERSON = "In Person"
    UNKNOWN = "Unknown"


class CompanySize(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    UNKNOWN = "Unknown"


class CompanyFundraisingRound(str, Enum):
    BOOTSTRAPPED = "Bootstrapped"
    PRE_SEED = "Pre-Seed"
    SEED = "Seed"
    SERIES_A = "Series A"
    SERIES_B = "Series B"
    SERIES_C = "Series C"
    UNKNOWN = "Unknown"


class Continents(str, Enum):
    EUROPE = "Europe"
    ASIA = "Asia"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    AFRICA = "Africa"
    ANTARCTICA = "Antarctica"


class CompanyDetails(BaseModel):
    hiring_company: Optional[str] = Field(None, description="Name of the hiring company, if mentioned")
    company_size: Optional[str] = Field(None, description="Size of the hiring company, if known")
    fundraising_status: Optional[str] = Field(None, description="Fundraising status of the company, if mentioned (e.g., amount, series type)")

class CommentStatus(str, Enum):
    JOB_OFFER = "job-offer"
    JOB_DEMAND = "job-demand"

class HNJobPosting(BaseModel):
    comment_status: CommentStatus = Field(description="Indicates if the comment is a job offer or a job demand")
    remote: JobLocationType = Field(JobLocationType.UNKNOWN, description="Whether the job is remote, hybrid, in person, or unknown")
    visa_sponsoring: bool = Field(False, description="Whether the job offers visa sponsoring or not. HAS TO BE A BOOLEAN VALUE!")
    states: List[str] = Field(default_factory=list, description="States where the job is located. Use the ISO 3166-2 code (e.g., 'NY' for New York)")
    countries: List[str] = Field(default_factory=list, description="Countries where the job is located. Use the ISO 3166-1 alpha-2 code (e.g., 'US' for United States)")
    continents: List[Continents] = Field(default_factory=list, description="Continents where the job is located")
    cities: List[str] = Field(default_factory=list, description="Cities where the job is located, if given.")
    tech_stack: List[str] = Field(default_factory=list, description="List of technologies forming the tech stack mentioned in the comment (specific databases, programming languages, libraries, etc.)")
    job_title: List[str] = Field(default_factory=list, description="Title of the job position, if mentioned")
    job_type: List[ContractType] = Field(default_factory=list, description="Type of job (e.g., full-time, part-time, contract, intern)")
    seniority_level: List[ExperienceLevel] = Field(default_factory=list, description="Seniority level required for the job")
    compensation_min: Optional[float] = Field(None, description="Minimum compensation amount in thousands of USD, if mentioned (e.g., 50 for $50k, 130 for $130k, etc)")
    compensation_max: Optional[float] = Field(None, description="Maximum compensation amount in thousands of USD, if mentioned (e.g., 150 for $150k, 300 for $300k, etc)")
    perks: List[str] = Field(default_factory=list, description="List of perks mentioned in the comment")
    hiring_company: str = Field(None, description="Name of the hiring company, if mentioned, otherwise N/A")
    company_size: CompanySize = Field(CompanySize.UNKNOWN, description="Size of the hiring company, if mentioned or if known at the time the job offer was published")
    fundraising_round: CompanyFundraisingRound = Field(CompanyFundraisingRound.UNKNOWN, description="Fundraising round of the company, if mentioned (e.g., Bootstrapped, Pre-Seed, Seed, Series A, Series B, Series C)")
    fundraising_amount: Optional[float] = Field(None, description="Fundraising amount of the company in millions of USD, if mentioned (e.g., 100 for $100M, 1000 for $1B, 10000 for $10B+)")

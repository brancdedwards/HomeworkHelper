"""
Subject Configuration Registry

Defines available subjects, their categories, and metadata.
This central configuration makes it easy to add new subjects without changing core logic.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class SubjectCategory(BaseModel):
    """Metadata for a subject category"""
    name: str
    display_name: str
    description: Optional[str] = None


class SubjectConfig(BaseModel):
    """Configuration for a subject"""
    key: str
    display_name: str
    categories: List[str]
    icon: str
    description: str
    grade_levels: List[str] = ["5th grade"]  # Default grade levels


# Subject Registry
SUBJECTS: Dict[str, SubjectConfig] = {
    'grammar': SubjectConfig(
        key='grammar',
        display_name='Grammar',
        categories=[
            'grammar_mechanics',
            'literary_devices',
            'parts_of_speech',
            'punctuation',
            'sentence_structure',
            'sentence_type',
            'vocabulary',
            'writing_quality'
        ],
        icon='📝',
        description='Grammar rules and writing mechanics',
        grade_levels=['3rd grade', '4th grade', '5th grade', '6th grade']
    ),
    'reading': SubjectConfig(
        key='reading',
        display_name='Reading Comprehension',
        categories=[
            'main_idea_theme',
            'inference_conclusions',
            'vocabulary_in_context',
            'text_structure_purpose'
        ],
        icon='📖',
        description='Reading comprehension and analysis',
        grade_levels=['3rd grade', '4th grade', '5th grade', '6th grade']
    )
}


# Category Display Names (for UI)
CATEGORY_DISPLAY_NAMES = {
    # Grammar categories
    'grammar_mechanics': 'Grammar Mechanics',
    'literary_devices': 'Literary Devices',
    'parts_of_speech': 'Parts of Speech',
    'punctuation': 'Punctuation',
    'sentence_structure': 'Sentence Structure',
    'sentence_type': 'Sentence Type',
    'vocabulary': 'Vocabulary',
    'writing_quality': 'Writing Quality',

    # Reading categories
    'main_idea_theme': 'Main Idea & Theme',
    'inference_conclusions': 'Inference & Conclusions',
    'vocabulary_in_context': 'Vocabulary in Context',
    'text_structure_purpose': 'Text Structure & Purpose'
}


def get_subject_config(subject_key: str) -> Optional[SubjectConfig]:
    """Get configuration for a subject by key"""
    return SUBJECTS.get(subject_key)


def get_all_subjects() -> List[SubjectConfig]:
    """Get list of all available subjects"""
    return list(SUBJECTS.values())


def is_valid_subject(subject_key: str) -> bool:
    """Check if a subject key is valid"""
    return subject_key in SUBJECTS


def is_valid_category(subject_key: str, category: str) -> bool:
    """Check if a category is valid for a given subject"""
    config = get_subject_config(subject_key)
    if not config:
        return False
    return category in config.categories


def normalize_category(category: str) -> str:
    """
    Normalize category from display format to database format
    Example: "Grammar Mechanics" -> "grammar_mechanics"
    """
    return category.lower().replace(' ', '_').replace('&', '').replace('  ', '_')


def get_category_display_name(category: str) -> str:
    """
    Get display name for a category
    Example: "grammar_mechanics" -> "Grammar Mechanics"
    """
    return CATEGORY_DISPLAY_NAMES.get(category, category.replace('_', ' ').title())


__all__ = [
    'SubjectConfig',
    'SubjectCategory',
    'SUBJECTS',
    'CATEGORY_DISPLAY_NAMES',
    'get_subject_config',
    'get_all_subjects',
    'is_valid_subject',
    'is_valid_category',
    'normalize_category',
    'get_category_display_name'
]

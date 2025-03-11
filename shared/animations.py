"""
Animations Module

This module provides various UI animation functions for a hacker-themed project,
inspired by Watch_Dogs, Cyberpunk, and Synthwave aesthetics.

All functions use the "apply_" prefix for universal reference and can be enabled/disabled via animations_enabled().

Available functions:
  - apply_fade_in(widget, duration): Fade-in animation.
  - apply_fade_out(widget, duration): Fade-out animation.
  - apply_slide_in(widget, start_pos, end_pos, duration): Slide animation.
  - apply_type_on_text(widget, full_text, interval): Type-on text effect.
  - apply_glow_effect(widget, color, blur_radius): Neon glow effect.
  - apply_glitch_effect(widget, duration): Brief glitch flicker effect.
  - apply_pulse_glow_effect(widget, color, blur_radius, duration): Pulsing neon glow.
  - apply_crt_scanline_effect(widget, duration): Subtle CRT scanline overlay effect.
  - apply_rapid_type_on_text(widget, full_text, interval): Rapid command input effect.
  - apply_boot_sequence_effect(widget, text_widget, boot_text_list, duration): Boot sequence text effect.
"""

import sys
from PyQt6.QtCore import QPropertyAnimation, QTimer, QEasingCurve, QPoint
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

# Global flag for animations.
ANIMATIONS_ENABLED = True

def animations_enabled():
    """Return True if animations are enabled; otherwise, False."""
    return ANIMATIONS_ENABLED

def apply_fade_in(widget: QWidget, duration: int = 500) -> QPropertyAnimation:
    if not animations_enabled():
        widget.setGraphicsEffect(None)
        return None
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    animation.start()
    return animation

def apply_fade_out(widget: QWidget, duration: int = 500) -> QPropertyAnimation:
    if not animations_enabled():
        widget.setGraphicsEffect(None)
        return None
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(1)
    animation.setEndValue(0)
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    animation.start()
    return animation

def apply_slide_in(widget: QWidget, start_pos: QPoint, end_pos: QPoint, duration: int = 500) -> QPropertyAnimation:
    if not animations_enabled():
        widget.move(end_pos)
        return None
    animation = QPropertyAnimation(widget, b"pos", widget)
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(end_pos)
    animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
    animation.start()
    return animation

def apply_type_on_text(widget: QWidget, full_text: str, interval: int = 50):
    if not animations_enabled():
        widget.setText(full_text)
        return
    widget.setText("")
    current_index = 0

    def update_text():
        nonlocal current_index
        current_index += 1
        widget.setText(full_text[:current_index])
        if current_index >= len(full_text):
            timer.stop()

    timer = QTimer(widget)
    timer.timeout.connect(update_text)
    timer.start(interval)

def apply_glow_effect(widget: QWidget, color: QColor = QColor(0, 255, 255), blur_radius: int = 20):
    if not animations_enabled():
        return None
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(color)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0)
    widget.setGraphicsEffect(effect)
    return effect

def apply_glitch_effect(widget: QWidget, duration: int = 300) -> QPropertyAnimation:
    """
    Applies a brief glitch flicker effect to the widget, simulating a momentary screen distortion.
    """
    if not animations_enabled():
        return None
    import random
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setKeyValueAt(0.0, 1)
    animation.setKeyValueAt(0.2, random.uniform(0.3, 0.7))
    animation.setKeyValueAt(0.5, 1)
    animation.setEasingCurve(QEasingCurve.Type.OutBounce)
    animation.start()
    return animation

def apply_pulse_glow_effect(widget: QWidget, color: QColor = QColor(0, 255, 255), blur_radius: int = 20, duration: int = 1000) -> QPropertyAnimation:
    """
    Applies a pulsing neon glow effect on the widget.
    The glow effect continuously pulses to attract attention.
    """
    if not animations_enabled():
        return None
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(color)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0)
    widget.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"blurRadius", widget)
    animation.setDuration(duration)
    animation.setStartValue(blur_radius)
    animation.setEndValue(blur_radius + 10)
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    animation.setLoopCount(-1)  # Loop indefinitely.
    animation.start()
    return animation

def apply_crt_scanline_effect(widget: QWidget, duration: int = 1200) -> QPropertyAnimation:
    """
    Applies a subtle CRT scanline effect by modulating the widget's opacity.
    """
    if not animations_enabled():
        return None
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.9)
    animation.setKeyValueAt(0.5, 0.6)
    animation.setEndValue(0.9)
    animation.setLoopCount(-1)
    animation.start()
    return animation

def apply_rapid_type_on_text(widget: QWidget, full_text: str, interval: int = 20):
    """
    Simulates a rapid command input effect by quickly revealing text.
    Suitable for console/terminal output.
    """
    if not animations_enabled():
        widget.setText(full_text)
        return
    widget.setText("")
    current_index = 0

    def update_text():
        nonlocal current_index
        current_index += 1
        widget.setText(full_text[:current_index])
        if current_index >= len(full_text):
            timer.stop()

    timer = QTimer(widget)
    timer.timeout.connect(update_text)
    timer.start(interval)

def apply_boot_sequence_effect(widget: QWidget, text_widget, boot_text_list: list, duration: int = 300):
    """
    Creates a boot sequence effect where text appears one line at a time,
    simulating a system startup.
    
    Args:
        widget (QWidget): The parent widget (for timer management).
        text_widget: The widget to display text (e.g., QLabel or QTextEdit).
        boot_text_list (list): List of strings for each line of the boot sequence.
        duration (int): Interval between lines in milliseconds.
    """
    if not animations_enabled():
        text_widget.setText("\n".join(boot_text_list))
        return

    text_widget.setText("")
    
    def show_next_line():
        nonlocal boot_text_list
        if boot_text_list:
            line = boot_text_list.pop(0)
            current_text = text_widget.text()
            if current_text:
                text_widget.setText(current_text + "\n" + line)
            else:
                text_widget.setText(line)
        else:
            timer.stop()
    
    timer = QTimer(widget)
    timer.timeout.connect(show_next_line)
    timer.start(duration)

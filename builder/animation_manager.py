# builder/animation_manager.py
class AnimationManager:
    def __init__(self):
        # By default, animations are enabled
        self.animations_enabled = True

    def enable_animations(self):
        self.animations_enabled = True

    def disable_animations(self):
        self.animations_enabled = False

    def are_animations_enabled(self):
        return self.animations_enabled

# Create a global instance that can be imported
animation_manager = AnimationManager()

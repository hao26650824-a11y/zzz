def draw_text(self, text, pos, **kwargs):
    # Ensure text_size is used for rendering
    self.label.text = text
    self.label.text_size = self.size
    self.label.pos = pos
    self.label.size = self.size
    self.label.refresh()
    # ... rest of your rendering logic goes here ...
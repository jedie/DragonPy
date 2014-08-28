class BaseExtension(object):
    def __init__(self, editor):
        self.editor = editor
        
        self.cfg=editor.cfg
        self.root = editor.root
        self.text = editor.text # ScrolledText() instance
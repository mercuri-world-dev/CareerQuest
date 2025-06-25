class DbResult:
  def __init__(self, success: bool, error: str = None, data: dict = {}):
    self.success = success
    self.error = error
    self.data = data

  def __repr__(self):
    return f"DbResult(success={self.success}, error='{self.error}, data={self.data}')"
class MovingAverage:

   def __init__(self, weight=0.5):
      """
      The weight (0<weight<=1) defines the proportion that the latest
      value contributes to the moving average.

      Higher values react more quickly to changes in the input data.

      Lower values smooth out outliers.
      """
      self.inited = False
      self._normalise(weight) # Make sure weight has a sensible value

   def average(self):
      """
      Retrun the current moving average.
      """
      if self.inited:
         return self.aver
      else:
         return None

   def add_value(self, value):
      """
      Add new value to moving avarage.
      """
      if self.inited:
         self.aver = ((value * self.weight) + (self.aver * (1-self.weight)))

      else:

         self.inited = True
         self.aver = value

   def reset(self, weight=0.5):
      """
      Reset moving average.
      """
      self.inited = False
      self._normalise(weight)

   def _normalise(self, weight):
      """
      Make sure weight has sensible values.
      """
      if weight <= 0:
         self.weight = 0.001
      elif weight > 1:
         self.weight = 1
      else:
         self.weight = weight

# ma = MovingAverage(0.5) # 0.5 weight for current reading

# print("moving average, weight 0.5")

# for v in range(10):
#    ma.add_value(30+(v/10.0))
#    print(ma.average())

# ma.reset(0.9) # Now 0.9 weight for current reading

# print("moving average, weight 0.9")

# for v in range(10):
#    ma.add_value(30+(v/10.0))
#    print(ma.average())

# print("moving average, weight 0.1")

# ma.reset(0.1) # Now 0.1 weight for current reading

# for v in range(10):
#    ma.add_value(30+(v/10.0))
#    print(ma.average())
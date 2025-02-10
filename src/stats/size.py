class Size:
    TINY = 2.5
    SMALL = 5
    MEDIUM = 5.1
    LARGE = 10
    HUGE = 15
    GARGANTUAN = 20

    _SIZE_CLASSES = [TINY, SMALL, MEDIUM, LARGE, HUGE, GARGANTUAN]

    def __init__(self, radius):
        if radius in self._SIZE_CLASSES:
            self._size_class = self._SIZE_CLASSES.index(radius)
        else:
            raise ValueError(f"Invalid size value ({radius})")
    
    @staticmethod
    def from_size_class(size_class):
        """Create a Size object directly from a size class value"""
        return Size(Size._SIZE_CLASSES[size_class])

    @property
    def radius(self):
        """Returns the size radius in feet"""
        # Note: Currently rounds up Tiny size to 5 feet to fill full grid space
        return max(5, int(self._SIZE_CLASSES[self._size_class]))
    
    @property
    def size_class(self):
        """Returns the size class value"""
        return self._size_class
    
    @size_class.setter
    def size_class(self, new_class):
        """Sets the size class value, throw error if invalid"""
        if new_class in range(6):
            self._size_class = new_class
        else:
            raise ValueError(f"Invalid size class value ({new_class})")
    


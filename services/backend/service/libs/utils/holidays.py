"""
Custom holiday utilities for the application.

This module provides custom holiday classes that modify the standard US holidays
to meet specific business requirements.
"""

from holidays.countries.united_states import UnitedStates


class USHolidaysWithoutBlackFriday(UnitedStates):
    """
    US Holidays excluding Black Friday (last Friday of November).
    
    The standard holidays library includes "Day After Thanksgiving" (Black Friday)
    as a holiday. This class removes it to allow business operations on that day.
    """
    
    def _populate(self, year):
        super()._populate(year)
        
        # Remove "Day After Thanksgiving" (Black Friday) from the holidays
        # Black Friday is the last Friday of November
        if "Day After Thanksgiving" in self.values():
            for date, name in list(self.items()):
                if name == "Day After Thanksgiving":
                    del self[date]

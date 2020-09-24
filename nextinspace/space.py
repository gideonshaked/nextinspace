"""The class definitions used to store data from the LL2 API."""

# Basic SpaceEvent parent class
class SpaceEvent:
    def __init__(self, mission_name, location, mission_date, mission_description, mission_type):
        self.mission_name = mission_name
        self.location = location
        self.mission_date = mission_date
        self.mission_description = mission_description
        self.mission_type = mission_type


class LaunchEvent(SpaceEvent):
    def __init__(self, mission_name, location, mission_date, mission_description, mission_type, rocket):
        super().__init__(mission_name, location, mission_date, mission_description, mission_type)
        self.rocket = rocket


# No additional attributes over SpaceEvent
class OtherEvent(SpaceEvent):
    pass


class Rocket:
    def __init__(
        self,
        name,
        payload_leo,
        payload_gto,
        liftoff_thrust,
        liftoff_mass,
        max_stages,
        successful_launches,
        consecutive_successful_launches,
        failed_launches,
        maiden_flight_date,
    ):

        self.name = name
        self.payload_leo = payload_leo
        self.payload_gto = payload_gto
        self.liftoff_thrust = liftoff_thrust
        self.liftoff_mass = liftoff_mass
        self.max_stages = max_stages
        self.successful_launches = successful_launches
        self.consecutive_successful_launches = consecutive_successful_launches
        self.failed_launches = failed_launches
        self.maiden_flight_date = maiden_flight_date

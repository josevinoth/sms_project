from django.db import models
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.driver_master_mod import  DrivermasterInfo

class MaintenanceInfo(models.Model):
    vehicle = models.ForeignKey(VehiclemasterInfo,on_delete=models.PROTECT,related_name="maintenance_records")
    make_model = models.CharField(max_length=100)
    registration_date = models.DateField(null=True, blank=True)
    chassis_no = models.CharField(max_length=50, null=True, blank=True)
    engine_no = models.CharField(max_length=50, null=True, blank=True)
    current_km = models.PositiveIntegerField()
    total_km_run = models.PositiveIntegerField()
    service_type = models.CharField(max_length=50)
    driver_name = models.ForeignKey(
        DrivermasterInfo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='driver_name'
    )
    est_delivery = models.DateTimeField()
    work_area = models.CharField(max_length=100)
    job_card_creator = models.CharField(max_length=100)
    job_card_created_on = models.DateTimeField()
    COMPLAINT_CHOICES = [
            ("", "-- Select --"),

            ("ac_engine", "AC ENGINE"),
            ("air_brake_system", "AIR BRAKE SYSTEM"),
            ("air_door", "AIR DOOR"),
            ("air_system", "AIR SYSTEM"),
            ("audio_video", "AUDIO & VIDEO"),
            ("body_work", "BODY WORK"),
            ("brake_system", "BRAKE SYSTEM"),
            ("clutch", "CLUTCH"),
            ("contractor", "CONTRACTOR"),
            ("cooling_systems", "COOLING SYSTEMS"),
            ("driver_left", "DRIVER LEFT"),
            ("electrical", "ELECTRICAL"),
            ("engine", "ENGINE"),
            ("engine_electrical_parts", "ENGINE ELECTRICAL PARTS"),
            ("front_axle", "FRONT AXLE"),
            ("fuel_feed_system", "FUEL FEED SYSTEM"),
            ("gear_box", "GEAR BOX"),
            ("general_maintenance", "GENERAL MAINTENANCE"),
            ("hydraulic_brake_system", "HYDRAULIC BRAKE SYSTEM"),
            ("intake_exhaust_system", "INTAKE & EXHAUST SYSTEM"),
            ("joint", "JOINT"),
            ("lubricating_system", "LUBRICATING SYSTEM"),
            ("non_r_m", "NON R & M"),
            ("painting", "PAINTING"),
            ("painting_works", "PAINTING WORKS"),
            ("periodic_service", "PERIODIC SERVICE"),
            ("rear_axle", "REAR AXLE"),
            ("retarder_electrical", "RETARDER BRAKE (ELECTRICAL)"),
            ("retarder_hydraulic", "RETARDER BRAKE (HYDRAULIC)"),
            ("steering", "STEERING"),
            ("suspension_system", "SUSPENSION SYSTEM"),
            ("tag_axle", "TAG AXLE (DEAD REAR AXLE)"),
            ("tank_work", "TANK WORK"),
            ("trailer", "TRAILER"),
            ("unscheduled_activities", "UNSCHEDULED ACTIVITIES"),
            ("vehicle_passing", "VEHICLE PASSING"),
            ("wheel", "WHEEL"),
            ("wheel_alignment", "WHEEL ALIGNMENT"),
        ]

    complaint = models.CharField(max_length=50,choices=COMPLAINT_CHOICES)
    description = models.TextField()
    technician = models.CharField(max_length=100, blank=True)
    estimated_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_card_no = models.CharField(max_length=20,null=True,blank=True,unique=True,)
    bay_no = models.CharField(max_length=10, null=True, blank=True)
    APPROVAL_STATUS_CHOICES = [
        (1, "Awaiting Manager Approval"),
        (2, "Awaiting Finance Approval"),
        (3, "Finance Approved"),
    ]
    approval_status = models.PositiveSmallIntegerField(choices=APPROVAL_STATUS_CHOICES,default=1)
    def __str__(self):
        # Ensure __str__ always returns a string even if job_card_no is None
        if self.job_card_no:
            return str(self.job_card_no)
        # Fallback to a descriptive string (use pk if available)
        return f"Maintenance{(' ' + str(self.pk)) if getattr(self, 'pk', None) else ''}"

from django.db import models
from .na_typeofreq_mod import Natypeofreq
from .my_user_mod import MyUser


class PkBomRuleMaster(models.Model):
    """Engineering rule matrix mapping Box Size (meters) x Weight (kg) to structural BOM specs."""
    TEMPLATE_CHOICES = (
        ('all', 'All Box Types'),
        ('plywood_box', 'Plywood Box'),
        ('pine_ply_box', 'Pine + Plywood Box'),
        ('skid_base', 'Skid Base Only'),
    )

    br_name = models.CharField(max_length=150)
    br_req_type = models.ForeignKey(Natypeofreq, on_delete=models.SET_NULL, null=True, blank=True)
    br_template_type = models.CharField(max_length=30, choices=TEMPLATE_CHOICES, default='all')

    # Size brackets in Meters (up to 4x4x4m and beyond)
    br_max_length_m = models.FloatField(default=4.0, help_text='Max Box Length in Meters')
    br_max_width_m = models.FloatField(default=4.0, help_text='Max Box Width in Meters')
    br_max_height_m = models.FloatField(default=4.0, help_text='Max Box Height in Meters')

    # Weight brackets in KG (e.g. 0-500, 501-1000, ..., 15001-20000)
    br_min_weight_kg = models.FloatField(default=0.0)
    br_max_weight_kg = models.FloatField(default=500.0)

    # Structural Base Specs
    br_base_runner_w_in = models.FloatField(default=3.0)
    br_base_runner_h_in = models.FloatField(default=4.0)
    br_base_runner_pitch_ft = models.FloatField(default=2.0, help_text='Max spacing between base runners in ft')
    br_lifting_runner_w_in = models.FloatField(default=4.0)
    br_lifting_runner_h_in = models.FloatField(default=1.5)
    br_lifting_runner_nos = models.IntegerField(default=2)
    br_deck_mat = models.CharField(max_length=20, choices=(('plywood', 'Plywood'), ('wood', 'Wood')), default='plywood')
    br_deck_thickness = models.FloatField(default=10.0, help_text='mm for plywood, inches for wood')

    # Walls & Top Specs
    br_wall_ply_mm = models.FloatField(default=10.0)
    br_frame_w_in = models.FloatField(default=4.0)
    br_frame_h_in = models.FloatField(default=1.0)
    br_batten_pitch_ft = models.FloatField(default=2.0, help_text='Vertical batten spacing in ft')
    br_mid_rail_height_ft = models.FloatField(default=4.0, help_text='Add horizontal mid-rail if height exceeds this (ft)')
    br_top_cross_width_ft = models.FloatField(default=3.5, help_text='Add extra top cross-frame if width exceeds this (ft)')

    # Supports & Arrest
    br_support_w_in = models.FloatField(default=3.0)
    br_support_h_in = models.FloatField(default=1.0)
    br_arrest_w_in = models.FloatField(default=4.0)
    br_arrest_h_in = models.FloatField(default=2.0)
    br_heavy_bracing = models.BooleanField(default=False)

    # Auto Nails & Consumables
    br_nail_kg_per_cft = models.FloatField(default=0.45)
    br_nail_kg_per_100sqft = models.FloatField(default=0.35)
    br_vci_overlap_pct = models.FloatField(default=15.0)
    br_strapping_pitch_ft = models.FloatField(default=2.5)

    br_priority = models.IntegerField(default=100)
    br_is_active = models.BooleanField(default=True)
    br_created_at = models.DateTimeField(auto_now_add=True, null=True)
    br_updated_at = models.DateTimeField(auto_now=True, null=True)
    br_updated_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['br_priority', 'br_min_weight_kg', 'br_max_length_m', 'br_max_width_m', 'br_max_height_m']

    def __str__(self):
        return f"{self.br_name} ({self.br_min_weight_kg}-{self.br_max_weight_kg} kg | <= {self.br_max_length_m}x{self.br_max_width_m}x{self.br_max_height_m}m)"


class PkBomRuleComponent(models.Model):
    """Dynamic component / terminology line belonging to a PkBomRuleMaster."""
    SECTION_CHOICES = (
        ('BASE', 'BASE'),
        ('LENGTH (2 SIDES)', 'LENGTH (2 SIDES)'),
        ('WIDTH (2 SIDES)', 'WIDTH (2 SIDES)'),
        ('TOP', 'TOP'),
        ('SUPPORTS & ARREST', 'SUPPORTS & ARREST'),
    )
    MAT_CHOICES = (
        ('wood', 'Wood'),
        ('plywood', 'Plywood'),
    )
    LEN_MODE_CHOICES = (
        ('L_FT', 'Box Length (ft)'),
        ('W_FT', 'Box Width (ft)'),
        ('H_FT', 'Box Height (ft)'),
        ('DIAG_LH_FT', 'Diagonal L-H (ft)'),
        ('FIXED', 'Fixed Length (ft)'),
    )
    WIDTH_MODE_CHOICES = (
        ('FIXED', 'Fixed (in)'),
        ('W_FT', 'Box Width (ft)'),
        ('H_FT', 'Box Height (ft)'),
    )
    QTY_MODE_CHOICES = (
        ('FIXED', 'Fixed Nos'),
        ('PITCH_L', 'By Length Pitch (ft)'),
        ('PITCH_W', 'By Width Pitch (ft)'),
        ('PITCH_L_2S', '2 Sides Length Pitch (ft)'),
        ('PITCH_W_2S', '2 Sides Width Pitch (ft)'),
    )

    brc_rule = models.ForeignKey(PkBomRuleMaster, on_delete=models.CASCADE, related_name='components')
    brc_section = models.CharField(max_length=40, choices=SECTION_CHOICES, default='BASE')
    brc_name = models.CharField(max_length=120, help_text='Component / Terminology e.g. BASE RUNNER, SADDLE SUPPORT')
    brc_mat = models.CharField(max_length=20, choices=MAT_CHOICES, default='wood')
    brc_len_mode = models.CharField(max_length=20, choices=LEN_MODE_CHOICES, default='L_FT')
    brc_len_val = models.FloatField(default=0.0, help_text='Used when Length Mode is Fixed')
    brc_width_mode = models.CharField(max_length=20, choices=WIDTH_MODE_CHOICES, default='FIXED')
    brc_width_val = models.FloatField(default=3.0, help_text='Width in inches (or ignored if W_FT/H_FT)')
    brc_thk_val = models.FloatField(default=1.0, help_text='Thickness in inches (wood) or mm (plywood)')
    brc_qty_mode = models.CharField(max_length=20, choices=QTY_MODE_CHOICES, default='FIXED')
    brc_qty_val = models.FloatField(default=2.0, help_text='Fixed Nos or Pitch in ft')
    brc_order = models.IntegerField(default=10)

    class Meta:
        ordering = ['brc_order', 'id']

    def __str__(self):
        return f"{self.brc_section}: {self.brc_name}"

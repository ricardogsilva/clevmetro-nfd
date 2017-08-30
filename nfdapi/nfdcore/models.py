# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import reversion
from django.contrib.gis.db.models.fields import PointField
from  django.utils import timezone
from django.contrib import admin
from django.db.models.fields.files import ImageField

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.fields import PositiveIntegerField
from PIL import Image
import os, time
from datetime import datetime
from nfdapi.settings import MEDIA_ROOT
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class DictionaryTable(models.Model):
    code = models.TextField(unique=True)
    name = models.TextField()
    
    def __str__(self):
        return "{0}-{1}".format(self.code, self.name) 
    
    class Meta:
        abstract = True

@python_2_unicode_compatible    
class DictionaryTableExtended(models.Model):
    code = models.TextField(unique=True)
    name = models.TextField()
    description = models.TextField()
    
    def __str__(self):
        return "{0}-{1}".format(self.code, self.name)
       
    class Meta:
        abstract = True

class OccurrenceCategory(DictionaryTable):
    # natural_area, plant, animal, fungus, slimemold
    main_cat = models.TextField()
    
    def natural_key(self):
        return (self.main_cat, self.code, self.name)

@reversion.register()    
class PointOfContact(models.Model):
    name = models.TextField(blank=False)
    affiliation = models.TextField(blank=True, null=True, default='')
    phone1 = models.TextField(blank=True, null=True, default='')
    phone2 = models.TextField(blank=True, null=True, default='')
    email = models.TextField(blank=True, null=True, default='')
    street_address = models.TextField(blank=True, null=True, default='')


class DayTime(DictionaryTable):
    pass

class Season(DictionaryTable):
    pass

class RecordOrigin(DictionaryTable):
    pass

class RecordingStation(DictionaryTable):
    pass

@reversion.register()
class OccurrenceObservation(models.Model):
    observation_date = models.DateField(blank=True, null=True)
    recording_datetime = models.DateField(blank=True, null=True)
    daytime = models.ForeignKey(DayTime, on_delete=models.SET_NULL, blank=True, null=True)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, blank=True, null=True)
    record_origin = models.ForeignKey(RecordOrigin, on_delete=models.SET_NULL, blank=True, null=True)
    #recording_station = models.ForeignKey(RecordingStation, on_delete=models.SET_NULL, blank=True, null=True)
    recording_station = models.TextField(blank=True, null=True, default='')
    reporter = models.ForeignKey(PointOfContact, on_delete=models.CASCADE, related_name='reporter')
    recorder = models.ForeignKey(PointOfContact, on_delete=models.CASCADE, blank=True, null=True, related_name='recorder')
    verifier = models.ForeignKey(PointOfContact, on_delete=models.CASCADE, blank=True, null=True, related_name='verifier')

PHOTO_UPLOAD_TO = 'images/%Y/%m/'
PHOTO_THUMB_SIZE=300

def get_thumbnail_and_date(input_image, input_path, thumbnail_size=(PHOTO_THUMB_SIZE, PHOTO_THUMB_SIZE)):
    """
    Create a thumbnail of an existing image
    :param input_image:
    :param thumbnail_size:
    :return:
    """
    if not input_image or input_image == "":
        return

    image = Image.open(input_image)
    date = None
    try:
        if image._getexif:
            for (exif_key, exif_value) in image._getexif().iteritems():
                if exif_key == 0x9003: # "DateTimeOriginal", decimal: 36867
                    date = datetime.strptime(exif_value, "%Y:%m:%d %H:%M:%S") # 2016:08:01 00:15:47 format
                    break
                elif exif_key == 0x0132: # "DateTime", decimal: 306
                    if not date:
                        date = datetime.strptime(exif_value, "%Y:%m:%d %H:%M:%S")
    except:
        pass
    if not date:
        date = timezone.now()
    image.thumbnail(thumbnail_size)
    basename = os.path.basename(input_path)
    name, ext = os.path.splitext(basename)
    thumb_filename = name + "_thumb" + ext
    thumb_fullpath = os.path.join(MEDIA_ROOT, time.strftime(PHOTO_UPLOAD_TO), thumb_filename)
    image.save(thumb_fullpath)
    return (thumb_fullpath  , date)

class Photograph(models.Model):
    image = ImageField(upload_to=PHOTO_UPLOAD_TO, height_field='image_height', width_field='image_width', max_length=1000)
    thumbnail = ImageField(upload_to=PHOTO_UPLOAD_TO, height_field='thumb_height', width_field='thumb_width', max_length=1000, blank=True)
    image_width = PositiveIntegerField()
    image_height = PositiveIntegerField()
    thumb_width = PositiveIntegerField(null=True)
    thumb_height = PositiveIntegerField(null=True)
    description = models.TextField(blank=True, null=True, default='')
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True, default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    occurrence_fk = models.PositiveIntegerField()
    occurrence = GenericForeignKey('content_type', 'occurrence_fk')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            (thumb, date) = get_thumbnail_and_date(self.image, self.image.path)
            self.thumbnail = thumb
            self.date = date
        except:
            pass
        super(Photograph, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

def get_occurrence_model(occurrence_maincat):
    try:
        if occurrence_maincat[0]=='n': # natural areas
            return OccurrenceNaturalArea
    except:
        pass
    return OccurrenceTaxon

class Occurrence(models.Model):
    geom = PointField()
    version = models.IntegerField(default=0)
    released_versions = models.IntegerField(default=0)
    occurrence_cat = models.ForeignKey(OccurrenceCategory, on_delete=models.SET_NULL, blank=True, null=True)
    released = models.BooleanField(default=False)
    inclusion_date = models.DateTimeField(default=timezone.now)
    observation = models.OneToOneField(OccurrenceObservation, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True

     
class CmStatus(DictionaryTableExtended):
    pass

    
class SRank(DictionaryTable):
    pass


class NRank(DictionaryTable):
    pass


class GRank(DictionaryTable):
    pass

class Element(models.Model):
    cm_status = models.ForeignKey(CmStatus, on_delete=models.SET_NULL, blank=True, null=True)
    s_rank = models.ForeignKey(SRank, on_delete=models.SET_NULL, blank=True, null=True)
    n_rank = models.ForeignKey(NRank, on_delete=models.SET_NULL, blank=True, null=True)
    g_rank = models.ForeignKey(GRank, on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        abstract = True

class RegionalStatus(DictionaryTableExtended):
    pass

class UsfwsStatus(DictionaryTable):
    pass

class IucnRedListCategory(DictionaryTable):
    pass

class ElementType(DictionaryTable):
    # alga, arachnid, bird, conifer, etc
    pass


class MushroomGroup(DictionaryTable):
    pass

@reversion.register()
class ElementSpecies(Element):
    native = models.NullBooleanField(default=True)
    oh_status = models.ForeignKey(RegionalStatus, on_delete=models.SET_NULL, blank=True, null=True)
    usfws_status = models.ForeignKey(UsfwsStatus, on_delete=models.SET_NULL, blank=True, null=True)
    iucn_red_list_category = models.ForeignKey(IucnRedListCategory, on_delete=models.SET_NULL, blank=True, null=True)
    other_code = models.TextField(blank=True)
    #species_category = models.ForeignKey(ElementType, on_delete=models.SET_NULL, blank=True, null=True)
    ibp_english = models.CharField(max_length=4, blank=True, default='')
    ibp_scientific = models.CharField(max_length=6, blank=True, default='')
    bblab_number = models.CharField(max_length=6, blank=True, default='')
    nrcs_usda_symbol = models.TextField(blank=True, default='')
    synonym_nrcs_usda_symbol = models.TextField(blank=True, default='')
    epa_numeric_code = models.TextField(blank=True, default='')
    mushroom_group = models.ForeignKey(MushroomGroup, on_delete=models.SET_NULL, blank=True, null=True)

@reversion.register()
class Species(models.Model):
    first_common = models.TextField()
    name_sci = models.TextField()
    tsn = models.PositiveIntegerField(null=True)
    synonym = models.TextField(blank=True, default='', null=True)
    second_common = models.TextField(blank=True, default='', null=True)
    third_common = models.TextField(blank=True, default='', null=True)
    family = models.TextField(blank=True, default='')
    family_common = models.TextField(blank=True, default='')
    phylum = models.TextField(blank=True, default='')
    phylum_common = models.TextField(blank=True, default='')
    element_species = models.ForeignKey(ElementSpecies, on_delete=models.CASCADE, blank=True, null=True)

@reversion.register()
class ElementNaturalAreas(Element):
    natural_area_code_nac = models.TextField(blank=True, default='')
    general_description = models.TextField(blank=True, default='')
    area = models.FloatField(null=True)
    landscape_position =  models.TextField(blank=True, default='') #FIXME

class Preservative(DictionaryTable):
    pass

class Storage(DictionaryTable):
    pass

class Repository(DictionaryTable):
    #FIXME: repository needs extra attributes (and maybe has to be managed as a non-dictionary table)
    pass

@reversion.register()
class Voucher(models.Model):
    voucher_number = models.PositiveIntegerField(null=True)
    specimen_collected = models.NullBooleanField(default=False)
    parts_collected = models.NullBooleanField(default=False)
    specimen_number = models.NullBooleanField(default=False)
    preservative = models.ForeignKey(Preservative, on_delete=models.SET_NULL, blank=True, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, blank=True, null=True)
    repository = models.TextField(null=True, blank=True, default='')


"""
class HabitatCategory(DictionaryTable):
    pass
"""

class AquaticHabitatCategory(DictionaryTable):
    pass

@reversion.register()
class TaxonDetails(models.Model):
    pass
    #habitat = models.ForeignKey(HabitatCategory, on_delete=models.SET_NULL, blank=True, null=True)

def get_details_class(category_code):
    if category_code=='co':
        return PlantDetails #FIXME
    elif category_code=='fe':
        return PlantDetails #FIXME
    elif category_code=='fl':
        return PlantDetails #FIXME
    elif category_code=='pl':
        return PlantDetails
    elif category_code=='mo':
        return PlantDetails # FIXME Moss
    elif category_code=='fu':
        return TaxonDetails #FIXME
    elif category_code=='sl':
        return SlimeMoldDetails
    elif category_code=='ln':
        return LandAnimalDetails
    elif category_code=='lk':
        return PondLakeAnimalDetails
    elif category_code=='st':
        return StreamAnimalDetails
    elif category_code=='we':
        return WetlandAnimalDetails

@reversion.register()
class OccurrenceTaxon(Occurrence):
    voucher = models.OneToOneField(Voucher, blank=True, null=True, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.SET_NULL, blank=True, null=True)
    details = models.OneToOneField(TaxonDetails, on_delete=models.CASCADE, null=True)
    photographs = GenericRelation(Photograph, object_id_field='occurrence_fk')
            
    def get_details_class(self):
        if self.occurrence_cat:
            return get_details_class(self.occurrence_cat.code)
        
    def get_details(self):
        """
        Gets the taxon details using the right model for the concrete instance. By default,
        Django will return the generic model instance (TaxonDetails) instead of an instance
        of LandAnimalDetails, PondLakeAnimalDetails, etc.
        """
        try:
            if self.details and self.occurrence_cat:
                return get_details_class(self.occurrence_cat.code).objects.get(pk=self.details.id)
        except:
            pass

@reversion.register()
class OccurrenceNaturalArea(Occurrence):
    natural_area_element = models.ForeignKey(ElementNaturalAreas, on_delete=models.SET_NULL, blank=True, null=True)
    photographs = GenericRelation(Photograph, object_id_field='occurrence_fk')

class Gender(DictionaryTable):
    pass

class Marks(DictionaryTable):
    pass

class DiseasesAndAbnormalities(DictionaryTable):
    pass

class TerrestrialSampler(DictionaryTable):
    pass

class AquaticSampler(DictionaryTable):
    pass


class TerrestrialStratum(DictionaryTable):
    pass

@reversion.register()
class AnimalLifestages(models.Model):
    egg = models.IntegerField()
    egg_mass = models.IntegerField()
    nest = models.IntegerField()
    early_instar_larva = models.IntegerField()
    larva = models.IntegerField()
    late_instar_larva = models.IntegerField()
    early_instar_nymph = models.IntegerField()
    nymph = models.IntegerField()
    late_instar_nymph = models.IntegerField()
    early_pupa = models.IntegerField()
    pupa = models.IntegerField()
    late_pupa = models.IntegerField()
    juvenile = models.IntegerField()
    immature = models.IntegerField()
    subadult = models.IntegerField()
    adult = models.IntegerField()
    adult_pregnant_or_young = models.IntegerField()
    senescent = models.IntegerField()
    unknown = models.IntegerField()
    na = models.IntegerField()

class AnimalDetails(TaxonDetails):
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, blank=True, null=True)
    marks = models.ForeignKey(Marks, on_delete=models.SET_NULL, blank=True, null=True)
    lifestages = models.OneToOneField(AnimalLifestages, on_delete=models.CASCADE, blank=True, null=True)
    diseases_and_abnormalities = models.ForeignKey(DiseasesAndAbnormalities, on_delete=models.SET_NULL, blank=True, null=True)
    #id_marks_description #FIXME
    class Meta:
        abstract = True

class AquaticAnimalDetails(AnimalDetails):
    sampler = models.ForeignKey(AquaticSampler, on_delete=models.SET_NULL, blank=True, null=True)
    class Meta:
        abstract = True

@reversion.register(follow=['taxondetails_ptr'])
class LandAnimalDetails(AnimalDetails):
    sampler = models.ForeignKey(TerrestrialSampler, on_delete=models.SET_NULL, blank=True, null=True)
    stratum = models.ForeignKey(TerrestrialStratum, on_delete=models.SET_NULL, blank=True, null=True)

class PondLakeType(DictionaryTable):
    pass

class PondLakeUse(DictionaryTable):
    pass

class ShorelineType(DictionaryTable):
    pass

class LakeMicrohabitat(DictionaryTable):
    pass

class LenticSize(models.Model):
    # FIXME: should we include it as additional tab instead of
    # integrating it on the PondLakeAnimalDetails tab??
    lentic_size_acres_aprox = models.IntegerField()
    lentic_size_squaremeters_aprox = models.IntegerField()
    lentic_size_acres_exact = models.DecimalField(max_digits=6, decimal_places=1)
    lentic_size_squaremeters_exact = models.DecimalField(max_digits=8, decimal_places=1)

    class Meta:
        abstract = True

@reversion.register()
class PondLakeAnimalDetails(AquaticAnimalDetails, LenticSize):
    pond_lake_name = models.TextField()
    pond_lake_type = models.ForeignKey(PondLakeType, on_delete=models.SET_NULL, blank=True, null=True)
    pond_lake_use = models.ForeignKey(PondLakeUse, on_delete=models.SET_NULL, blank=True, null=True)
    shoreline_type = models.ForeignKey(ShorelineType, on_delete=models.SET_NULL, blank=True, null=True)
    microhabitat = models.ForeignKey(LakeMicrohabitat, on_delete=models.SET_NULL, blank=True, null=True)
    microhabitat_comments = models.TextField()
    

class StreamDesignatedUse(DictionaryTable):
    pass

class ChannelType(DictionaryTable):
    pass

class HmfeiLocalAbundance(DictionaryTable):
    pass

class LoticHabitatType(DictionaryTable):
    pass

@reversion.register()
class StreamSubstracte(models.Model):
    artificial = models.FloatField()
    bedrock = models.FloatField()
    boulder = models.FloatField()
    boulder_slab = models.FloatField()
    clay_hardpan = models.FloatField()
    cobble = models.FloatField()
    fine_detritus = models.FloatField()
    gravel = models.FloatField()
    leafpack_woody_debris = models.FloatField()
    muck = models.FloatField()
    sand = models.FloatField()
    silt = models.FloatField()

class WaterFlowType(DictionaryTable):
    pass

@reversion.register()
class StreamAnimalDetails(AquaticAnimalDetails):
    stream_name_1 = models.TextField()
    stream_name_2 = models.TextField(blank=True, null=True)
    pemso_code = models.TextField(blank=True, null=True)
    designated_use = models.ForeignKey(StreamDesignatedUse, on_delete=models.SET_NULL, blank=True, null=True)
    channel_type = models.ForeignKey(ChannelType, on_delete=models.SET_NULL, blank=True, null=True)
    hmfei_local_abundance = models.ForeignKey(HmfeiLocalAbundance, on_delete=models.SET_NULL, blank=True, null=True)
    lotic_habitat_type = models.ForeignKey(LoticHabitatType, on_delete=models.SET_NULL, blank=True, null=True)
    substrate = models.ForeignKey(StreamSubstracte, on_delete=models.CASCADE, blank=True, null=True)
    water_flow_type = models.ForeignKey(WaterFlowType, on_delete=models.SET_NULL, blank=True, null=True)

class WetlandType(DictionaryTable):
    pass

class WetlandLocation(DictionaryTable):
    pass

@reversion.register()
class WetlandVetegationStructure(models.Model):
    buttonbush = models.FloatField()
    cattail = models.FloatField()
    ferns = models.FloatField()
    forbs = models.FloatField()
    phragmites = models.FloatField()
    sedges = models.FloatField()

class WetlandConnectivity(DictionaryTable):
    pass

class WaterSource(DictionaryTable):
    pass

class WetlandHabitatFeature(DictionaryTable):
    pass

@reversion.register()  
class WetlandAnimalDetails(AquaticAnimalDetails, LenticSize):
    wetland_name = models.TextField()
    wetland_type = models.ForeignKey(WetlandType, on_delete=models.SET_NULL, blank=True, null=True)
    active_management = models.NullBooleanField(blank=True, null=True)
    wetland_location = models.ForeignKey(WetlandLocation, on_delete=models.SET_NULL, blank=True, null=True)
    vegetation = models.OneToOneField(WetlandVetegationStructure, on_delete=models.CASCADE, blank=True, null=True)
    connectivity = models.ForeignKey(WetlandConnectivity, on_delete=models.SET_NULL, blank=True, null=True)
    water_source = models.ForeignKey(WaterSource, on_delete=models.SET_NULL, blank=True, null=True)
    habitat_feature = models.ForeignKey(WetlandHabitatFeature, on_delete=models.SET_NULL, blank=True, null=True)

class SlimeMoldLifestages(DictionaryTable):
    pass

class SlimeMoldClass(DictionaryTableExtended):
    pass

class SlimeMoldMedia(DictionaryTable):
    pass

@reversion.register()
class SlimeMoldDetails(TaxonDetails):
    #lifestages = models.ForeignKey(SlimeMoldLifestages, on_delete=models.SET_NULL, blank=True, null=True)
    slime_mold_class = models.ForeignKey(SlimeMoldClass, on_delete=models.SET_NULL, blank=True, null=True)
    slime_mold_media = models.ForeignKey(SlimeMoldMedia, on_delete=models.SET_NULL, blank=True, null=True)

class PlantDetails(TaxonDetails):
    """
    AQUI ME QUEDO: HAY QUE DEFINIR MODELO PARA PlaintDetails y sus subclases
    """
    pass


plants = ['plant', 'plant_conifer_or_ally', 'plant_fern_or_ally',
          'plant_flowering_plant', 'plant_moss_or_ally']
slime_mold = ['slime_mold']
fungus = ['fungus']
animals = ['animal', 'animal_aquatic_animal', 'animal_land_animal',
           'animal_pond_lake_animal', 'animal_stream_animal', 'animal_wetland_animal']
natural_area = ['natural_area']
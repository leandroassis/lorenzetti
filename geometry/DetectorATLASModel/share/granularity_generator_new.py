

import os
import json
import logging
import numpy as np
from math import *
from pprint import pprint

from Gaugi import Logger
from Gaugi.messenger.macros import *

# everything to mm
m = 1000
cm = 10
mm = 1
pi = np.pi

eps = 1e-4

def xy_z_to_theta( r_xy, r_z ):
  if r_z!=0:
    theta = np.arctan2(  r_xy , r_z )
  else:
    theta = np.pi/2
  return theta

def theta_to_eta( theta ):
  try:
    eta = -np.log(np.tan( theta/2. ) )
  except:
    eta = -np.log(np.tan( (theta+np.pi)/2.) )
  return eta

def xy_z_to_eta( r_xy, z ):
  return theta_to_eta( xy_z_to_theta( r_xy, z ) )




#
# Lateral segmentation
#
class LateralSegmentation(object):
  
  def __init__( self, rMin, rMax
              , delta_eta, delta_phi
              , z_min, z_max
              , eta_min = None, eta_max = None, sample_id=None ):
    self.delta_eta = delta_eta
    self.delta_phi = delta_phi
    self.sample_id = sample_id
    self.eta_min = eta_min 
    self.eta_max = eta_max
    self.rMin = rMin
    self.rMax = rMax
    self.zMin = z_min
    self.zMax = z_max


  #
  # eta min
  #
  @property
  def eta_min(self):
    return self._eta_min

  @eta_min.setter
  def eta_min(self, value):
    self._eta_min = value

  #
  # eta max
  #
  @property
  def eta_max(self):
    return self._eta_max

  @eta_max.setter
  def eta_max(self, value):
    self._eta_max = value

  #
  # z min
  #
  @property
  def zMin(self):
    return self._zMin

  @zMin.setter
  def zMin(self, value):
    self._zMin = value
    if self.eta_min is None: 
      self._eta_min = xy_z_to_eta( self.rMax, self._zMin )

  #
  # z max
  #
  @property
  def zMax(self):
    return self._zMax

  @zMax.setter
  def zMax(self, value):
    self._zMax = value
    if self.eta_max is None: 
      self._eta_max = xy_z_to_eta( self.rMin, self._zMax )
  
  #
  # phi min/max
  #
  @property
  def phi_min(self):
    return -np.pi

  @property
  def phi_max(self):
    return np.pi

  #
  # Get the eta bins for all segmentations
  #
  @property
  def eta_bins(self):
    eta_bins = np.arange( self.eta_min, self.eta_max  + eps, step = self.delta_eta ) 
    return np.concatenate ( [np.flip(-eta_bins[1::]), eta_bins] )
 
  #
  # Get the phi bins for all segmentations
  #
  @property
  def phi_bins(self):
    return np.arange( self.phi_min, self.phi_max  + eps, step = self.delta_phi ) 


  #
  # Compute all eta cell centers
  #
  def compute_eta_cell_centers(self):
    # the max value in np.arange is protected since this array can pass the eta_max when we add the delta_eta
    positive_eta = np.arange( 
        self.eta_min + self.delta_eta/2, 
        self.eta_max - self.delta_eta/2 + eps, 
        step = self.delta_eta )

    return np.concatenate( [np.flip(-positive_eta), positive_eta] )

  #
  # Compute all phi cell centers
  #
  def compute_phi_cell_centers(self):
    positive_phi = np.arange( 
        0. + self.delta_phi/2,  
        np.pi - self.delta_phi/2 + eps,
        step = self.delta_phi )
    return np.concatenate ( [np.flip(-positive_phi), positive_phi] )


  def __str__(self):
    return 

  def __repr__(self):
    return self.__class__.__name__ + str(self)



  #
  # Dump
  #
  def dump(self, output, seg_id):
    
    with open( output, 'w' ) as f:

      f.write("# sample segmentation eta phi delta_eta delta_phi rmin rmax zmin zmax\n")
      eta_bins = self.eta_bins
      phi_bins = self.phi_bins
        
      # dump layer information
      s = "config {SAMPLE} {SEGMENTATION} {ETA_MIN} {ETA_MAX} {RMIN} {RMAX} {ZMIN} {ZMAX}\n".format( 
        SAMPLE        = self.sample_id,
        SEGMENTATION  = seg_id,
        ETA_MIN       = round(self.eta_min,8),
        ETA_MAX       = round(self.eta_max,8),
        RMIN          = round(self.rMin,8),
        RMAX          = round(self.rMax,8),
        ZMIN          = round(self.zMin,8),
        ZMAX          = round(self.zMax,8),
      )
      f.write(s)

      # dump eta bins
      s = "eta_bins"
      for value in eta_bins:  s+=' '+str(round(value,4))
      s+='\n'
      f.write(s)

      # Dump phi bins
      s = "phi_bins"
      for value in phi_bins:  s+=' '+str(round(value,4))
      s+='\n'
      f.write(s)

      eta_centers = self.compute_eta_cell_centers()
      phi_centers = self.compute_phi_cell_centers()
      for  eta_idx , eta in enumerate(eta_centers):
        for phi_idx , phi in enumerate(phi_centers):
         
          hash_id = int(self.sample_id*1e7 + seg_id*1e6 + (eta_idx*(len(phi_bins)-1) + phi_idx ) )
          s = "cell {SAMPLE} {ETA} {PHI} {DETA} {DPHI} {RMIN} {RMAX} {ZMIN} {ZMAX} {CELL_HASH}\n".format( 
            SAMPLE    = self.sample_id,
            ETA       = round(eta,8),
            PHI       = round(phi,8),
            DETA      = round(self.delta_eta,8),
            DPHI      = round(self.delta_phi,8),
            RMIN      = round(self.rMin,8),
            RMAX      = round(self.rMax,8),
            ZMIN      = round(self.zMin,8),
            ZMAX      = round(self.zMax,8),
            CELL_HASH = hash_id,
          )
          f.write(s)






class Layer(object):

  def __init__(self, name, sample_id, segmentations ):
    self.layer = name 
    self.sample_id = sample_id
    if not isinstance(segmentations,(list,tuple)):
      segmentations = [segmentations]
    # set the layer id by hand
    for seg in segmentations:
      seg.sample_id = sample_id
    self.segmentations = segmentations


  #
  # Dump layer
  #
  def dump(self):
    for seg_idx, seg in enumerate(self.segmentations):
      output = 'detector_sample_%d_seg_%d.dat' % (self.sample_id, seg_idx)
      seg.dump(output, seg_idx)







class SingleSegmentationLayer(object):
  def __init__(self, name, sample_id, **kw):
    segmentation = LateralSegmentation(sample_id = sample_id, **kw)
    self.layer = Layer( name, sample_id, segmentations = segmentation)

  def dump(self):
    self.layer.dump()




#
# Build the ATLAS detector here
#




barrel_ps_nominal_radius  = 146*cm
barrel_em_nominal_radius  = 150*cm
barrel_had_nominal_radius = 228.3*cm
extended_barrel_nominal_z = 2.83*m

barrel_em_calo_radius = np.array( [1.1*cm, 9.6*cm, 33*cm, 5.4*cm] )
barrel_had_calo_radius = np.array( [40*cm, 110*cm, 50*cm] )

endcap_start_z = 3704.*mm;

emec_dead_material_z = 78.*mm;
emec_start_radius = 302.*mm
emec_end_radius = 2032.*mm
emec_start_z = endcap_start_z+emec_dead_material_z;

hec_start_z = 4262*mm;
hec_start_radius = np.array([372.*mm,475.*mm, 475.*mm])
hec_end_radius = np.array([2030.*mm]*3)

emec_layer_z = np.array( [96*mm, 330*mm, 54*mm] )
hec_layer_z =  np.array( [289*mm, 536*mm, 969.5*mm] )




psb = SingleSegmentationLayer( name = "PSB",
    sample_id = 0,
    rMin = barrel_ps_nominal_radius, 
    rMax = barrel_ps_nominal_radius + barrel_em_calo_radius[0].sum(),
    delta_eta = 0.025, 
    delta_phi = pi/32,
    z_min = 0*m, 
    z_max = 3.4*m )

emb1 = SingleSegmentationLayer(
    name = "EMB1",
    sample_id = 1,
    rMin = barrel_em_nominal_radius, 
    rMax = barrel_em_nominal_radius + barrel_em_calo_radius[1:2].sum(),
    delta_eta = 0.00325, 
    delta_phi = pi/32,
    z_min = 0*m, 
    z_max = 3.4*m )

emb2 = SingleSegmentationLayer(
    name = "EMB2",
    sample_id = 2,
    rMin = barrel_em_nominal_radius + barrel_em_calo_radius[1:2].sum(), 
    rMax = barrel_em_nominal_radius + barrel_em_calo_radius[1:3].sum(),
    delta_eta = 0.025, 
    delta_phi = pi/128,
    z_min = 0*m, 
    z_max = 3.4*m )

emb3 = SingleSegmentationLayer(
    name = "EMB3",
    sample_id = 3,
    rMin = barrel_em_nominal_radius + barrel_em_calo_radius[1:3].sum(), 
    rMax = barrel_em_nominal_radius + barrel_em_calo_radius[1:4].sum(),
    delta_eta = 0.050, 
    delta_phi = pi/128,
    z_min = 0*m, 
    z_max = 3.4*m )

tilecal1 = SingleSegmentationLayer(
    name = "TileCal1",
    sample_id = 4,
    rMin = barrel_had_nominal_radius, 
    rMax = barrel_had_nominal_radius + barrel_had_calo_radius[1:2].sum(),
    delta_eta = 0.1, 
    delta_phi = pi/32,
    z_min = 0*m, 
    z_max = 3.024*m )

tilecal2 = SingleSegmentationLayer(
    name = "TileCal2",
    sample_id = 5,
    rMin = barrel_had_nominal_radius + barrel_had_calo_radius[1:2].sum(), 
    rMax = barrel_had_nominal_radius + barrel_had_calo_radius[1:3].sum(),
    delta_eta = 0.1, 
    delta_phi = pi/32,
    z_min = 0*m, 
    z_max = 3.024*m )

tilecal3 = SingleSegmentationLayer(
    name = "TileCal3",
    sample_id = 6,
    rMin = barrel_had_nominal_radius + barrel_had_calo_radius[1:3].sum(), 
    rMax = barrel_had_nominal_radius + barrel_had_calo_radius[1:4].sum(),
    delta_eta = 0.2, 
    delta_phi = pi/32,
    z_min = 0*m, 
    z_max = 3.024*m )

tileext1 = SingleSegmentationLayer(
    name = "TileExt1",
    sample_id = 7,
    rMin = barrel_had_nominal_radius, 
    rMax = barrel_had_nominal_radius + barrel_had_calo_radius[1:2].sum(),
    delta_eta = 0.1, 
    delta_phi = pi/32,
    z_min = endcap_start_z, 
    z_max = endcap_start_z + extended_barrel_nominal_z )

tileext2 = SingleSegmentationLayer(
    name = "TileExt2",
    sample_id = 8,
    rMin = barrel_had_nominal_radius + barrel_had_calo_radius[1:2].sum(), 
    rMax = barrel_had_nominal_radius + barrel_had_calo_radius[1:3].sum(),
    delta_eta = 0.1, 
    delta_phi = pi/32,
    z_min = endcap_start_z, 
    z_max = endcap_start_z + extended_barrel_nominal_z )

tileext3 = SingleSegmentationLayer(
    name = "TileExt3",
    sample_id = 9,
    rMin = barrel_had_nominal_radius + barrel_had_calo_radius[1:3].sum(), 
    rMax = barrel_had_nominal_radius + barrel_had_calo_radius[1:4].sum(),
    delta_eta = 0.2, 
    delta_phi = pi/32,
    z_min = endcap_start_z,
    z_max = endcap_start_z + extended_barrel_nominal_z )





emec1 = Layer(
    name = "EMEC1",
    sample_id = 10,
    segmentations = [
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.00325, 
        delta_phi = pi/32,
        z_min = emec_start_z + emec_layer_z[0:0].sum(), 
        z_max = emec_start_z + emec_layer_z[0:1].sum(),
        eta_min = 1.375, 
        eta_max = 1.8 ),
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.025/4, 
        delta_phi = pi/32,
        z_min = emec_start_z + emec_layer_z[0:0].sum(), 
        z_max = emec_start_z + emec_layer_z[0:1].sum(),
        eta_min = 1.8, 
        eta_max = 2.0 ),
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.00650, 
        delta_phi = pi/32,
        z_min = emec_start_z + emec_layer_z[0:0].sum(), 
        z_max = emec_start_z + emec_layer_z[0:1].sum(),
        eta_min = 2.0, 
        eta_max = 2.37 ),
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.1, 
        delta_phi = pi/32,
        z_min = emec_start_z + emec_layer_z[0:0].sum(), 
        z_max = emec_start_z + emec_layer_z[0:1].sum(),
        eta_min = 2.37, 
        eta_max = 3.2 ),
    ],
)

emec2 = Layer(
    name = "EMEC2",
    sample_id = 11,
    segmentations = [
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.025,
        delta_phi = pi/128,
        z_min = emec_start_z + emec_layer_z[0:1].sum(), 
        z_max = emec_start_z + emec_layer_z[0:2].sum(),
        eta_min = 1.35, 
        eta_max = 2.5 ),
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.1,
        delta_phi = pi/32,
        z_min = emec_start_z + emec_layer_z[0:1].sum(), 
        z_max = emec_start_z + emec_layer_z[0:2].sum(),
        eta_min = 2.5, 
        eta_max = 3.2 ),
    ],
)

emec3 = Layer(
    name = "EMEC3",
    sample_id = 12,
    segmentations = [
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.050,
        delta_phi = pi/128,
        z_min = emec_start_z + emec_layer_z[0:2].sum(), 
        z_max = emec_start_z + emec_layer_z[0:3].sum(),
        eta_min = 1.35, 
        eta_max = 2.5 ),
      LateralSegmentation( 
        rMin = emec_start_radius, 
        rMax = emec_end_radius,
        delta_eta = 0.1,
        delta_phi = pi/32,
        z_min = emec_start_z + emec_layer_z[0:2].sum(), 
        z_max = emec_start_z + emec_layer_z[0:3].sum(),
        eta_min = 2.5, 
        eta_max = 3.2 ),
    ],
)

hec1 = Layer(
    name = "HEC1",
    sample_id = 13,
    segmentations = [
      LateralSegmentation( 
        rMin = hec_start_radius[0], 
        rMax = hec_end_radius[0],
        delta_eta = 0.1,
        delta_phi = pi/32,
        z_min = hec_start_z + hec_layer_z[0:0].sum(), 
        z_max = hec_start_z + hec_layer_z[0:1].sum(),
        eta_min = 1.5, 
        eta_max = 2.5 ),
      LateralSegmentation( 
        rMin = hec_start_radius[0], 
        rMax = hec_end_radius[0],
        delta_eta = 0.2,
        delta_phi = pi/16,
        z_min = hec_start_z + hec_layer_z[0:0].sum(), 
        z_max = hec_start_z + hec_layer_z[0:1].sum(),
        eta_min = 2.5, 
        eta_max = 3.2 ),
    ],
)

hec2 = Layer(
    name = "HEC2",
    sample_id = 14,
    segmentations = [
      LateralSegmentation( 
        rMin = hec_start_radius[1], 
        rMax = hec_end_radius[1],
        delta_eta = 0.1,
        delta_phi = pi/32,
        z_min = hec_start_z + hec_layer_z[0:1].sum(), 
        z_max = hec_start_z + hec_layer_z[0:2].sum(),
        eta_min = 1.5, 
        eta_max = 2.5 ),
      LateralSegmentation( 
        rMin = hec_start_radius[1], 
        rMax = hec_end_radius[1],
        delta_eta = 0.2,
        delta_phi = pi/16,
        z_min = hec_start_z + hec_layer_z[0:1].sum(), 
        z_max = hec_start_z + hec_layer_z[0:2].sum(),
        eta_min = 2.5, 
        eta_max = 3.2 ),
    ],
)

hec3 = Layer(
    name = "HEC3",
    sample_id = 14,
    segmentations = [
      LateralSegmentation( 
        rMin = hec_start_radius[2], 
        rMax = hec_end_radius[2],
        delta_eta = 0.1,
        delta_phi = pi/32,
        z_min = hec_start_z + hec_layer_z[0:2].sum(), 
        z_max = hec_start_z + hec_layer_z[0:3].sum(),
        eta_min = 1.5, 
        eta_max = 2.5 ),
      LateralSegmentation( 
        rMin = hec_start_radius[2], 
        rMax = hec_end_radius[2],
        delta_eta = 0.2,
        delta_phi = pi/16,
        z_min = hec_start_z + hec_layer_z[0:2].sum(), 
        z_max = hec_start_z + hec_layer_z[0:3].sum(),
        eta_min = 2.5, 
        eta_max = 3.2 ),
    ],
)

em_barrel = [psb, emb1, emb2, emb3]
had_barrel = [ tilecal1, tilecal2, tilecal3
             , tileext1, tileext2, tileext3 ]
emec = [emec1, emec2, emec3]
hec = [hec1, hec2, hec3]

all_calo = [em_barrel, had_barrel, emec, hec]


for calo in all_calo:
  for layer in calo:
    layer.dump()

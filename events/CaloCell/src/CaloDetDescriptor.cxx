
#include "CaloCell/CaloDetDescriptor.h"
#include "CaloCell/enumeration.h"
#include "G4PhysicalConstants.hh"
#include "G4SystemOfUnits.hh"

using namespace xAOD;



CaloDetDescriptor::CaloDetDescriptor( 
                  float eta, 
                  float phi, 
                  float deta, 
                  float dphi, 
                  float radius_min, 
                  float radius_max,
                  unsigned int hash,
                  CaloSampling sampling, 
                  Detector detector,
                  float bc_duration,
                  int bc_nsamples,
                  int bcid_start,
                  int bcid_end,
                  int bcid_truth ):
  m_sampling(sampling),
  m_detector(detector),
  m_eta(eta),
  m_phi(phi),
  m_deta(deta),
  m_dphi(dphi),
  m_radius_min(radius_min),
  m_radius_max(radius_max),
  m_energy(0),
  m_truthEnergy(0),
  /* Bunch crossing information */
  m_bcid_start( bcid_start ),
  m_bcid_end( bcid_end ),
  m_bc_nsamples( bc_nsamples ),
  m_bcid_truth( bcid_truth ),
  m_bc_duration( bc_duration ),
  m_energySamples( (bcid_end-bcid_start+1)*bc_nsamples, 0 ),
  m_hash(hash)
{
  // Initalize the time vector using the bunch crossing informations
  float start = ( m_bcid_start - 0.5 ) * m_bc_duration;
  float step  = m_bc_duration / m_bc_nsamples;
  int total   = (m_bcid_end - m_bcid_start+1) * m_bc_nsamples + 1;
  for (int t = 0; t < total; ++t) {
    m_time.push_back( (start + step*t) );
  }
}


void CaloDetDescriptor::clear()
{
  m_energy=0.0;
  m_truthEnergy=0.0;
  for (std::vector<float>::iterator it = m_energySamples.begin(); it < m_energySamples.end(); it++)
  {
    *it=0.0;
  }
}


void CaloDetDescriptor::Fill( const G4Step* step )
{
  // Get total energy deposit
  float edep = (float)step->GetTotalEnergyDeposit();
  G4StepPoint* point = step->GetPreStepPoint();
  // Get the position
  G4ThreeVector pos = point->GetPosition();
  // Get the particle time
  float t = (float)point->GetGlobalTime() / ns;
  // Get the bin index into the time vector
  int sample = findIndex(t);
  

  if ( sample != -1 ){
    m_energySamples[sample]+=(edep/MeV);
  }

  if ( t >= ( (m_bcid_truth-1)*m_bc_duration) && t < ((m_bcid_truth+1)*m_bc_duration)){
    m_truthEnergy+=(edep/MeV);
  }
}



int CaloDetDescriptor::findIndex( float value) const 
{
  auto binIterator = std::adjacent_find( m_time.begin(), m_time.end(), [=](float left, float right){ return left < value and value <= right; }  );
  if ( binIterator == m_time.end() ) return -1;
  return  binIterator - m_time.begin();
}


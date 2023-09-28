

#include "TruthParticle/TruthParticle.h"


using namespace xAOD;


TruthParticle::TruthParticle():
  m_pdgid(0),
  m_e(0),
  m_et(0),
  m_eta(0),
  m_phi(0),
  m_px(0),
  m_py(0),
  m_pz(0),
  m_vtx_x(0),
  m_vtx_y(0),
  m_vtx_z(0)
  // m_seed_eta(0),
  // m_seed_phi(0),
  // m_seed_etot(0),
  // m_seed_ettot(0)
{;}


TruthParticle::TruthParticle( float e, float et, float eta, float phi , 
                              float px, float py, float pz, int pdgid, 
                              float vx, float vy, float vz):
                              // float seedEta, float seedPhi, float seedEtot, float seedEttot,
                                
  m_pdgid(pdgid),
  m_e(e),
  m_et(et),
  m_eta(eta),
  m_phi(phi),
  m_px(px),
  m_py(py),
  m_pz(pz),
  m_vtx_x(vx),
  m_vtx_y(vy),
  m_vtx_z(vz)
  // m_seed_eta(seedEta),
  // m_seed_phi(seedPhi),
  // m_seed_etot(seedEtot),
  // m_seed_ettot(seedEttot)
{;}












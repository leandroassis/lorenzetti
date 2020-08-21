#ifndef CaloClusterMaker_h
#define CaloClusterMaker_h

#include "CaloCell/enumeration.h"
#include "GaugiKernel/StatusCode.h"
#include "GaugiKernel/DataHandle.h"
#include "GaugiKernel/Algorithm.h"
#include "CaloCell/CaloCellContainer.h"
#include "CaloCluster/CaloClusterContainer.h"
#include "TruthParticle/TruthParticleContainer.h"
#include "EventInfo/EventInfoContainer.h"
#include "ShowerShapes.h"


class CaloClusterMaker : public Gaugi::Algorithm
{

  public:
    /** Constructor **/
    CaloClusterMaker( std::string );
    
    virtual ~CaloClusterMaker();
    
    virtual StatusCode initialize() override;

    /*! Book all histograms into the current storegate **/
    virtual StatusCode bookHistograms( SG::EventContext &ctx ) const override;
    
    virtual StatusCode pre_execute( SG::EventContext &ctx ) const override;
    
    virtual StatusCode execute( SG::EventContext &ctx , const G4Step *step) const override;
    
    virtual StatusCode post_execute( SG::EventContext &ctx ) const override;
    
    virtual StatusCode fillHistograms( SG::EventContext &ctx ) const override;
    
    virtual StatusCode finalize() override;



  private:
 
    
    void fillCluster( SG::EventContext &ctx,  xAOD::CaloCluster *clus, std::string key ) const;
    
    float dR( float eta1, float phi1, float eta2, float phi2 ) const;
 
    std::vector< std::pair<xAOD::TruthParticle*,xAOD::CaloCluster*> > getAllClusters( SG::EventContext &ctx , std::string key ) const;
    
    float sumEnergy(const xAOD::CaloCluster *clus, CaloSampling::CaloLayer layer, unsigned eta_ncell, unsigned phi_ncell, bool raw=false) const;
      
    // input keys
    std::string m_cellsKey;
    std::string m_eventKey;
    
    // output keys
    std::string m_truthKey;
    std::string m_clusterKey;

    float m_etaWindow;
    float m_phiWindow;
    std::string m_histPath;

    // Shower shaper calculator
    ShowerShapes *m_showerShapes;

    float m_minCenterEnergy;


};

#endif





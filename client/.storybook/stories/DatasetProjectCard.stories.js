import React from 'react'
import 'regenerator-runtime/runtime'
import { Box} from 'grommet'
import { DatasetProjectCard } from 'components/DatasetProjectCard'

// NOTE: Mock data ("data" data structure copied from the current BE test)
const datasets = [
    {
      id: 'UUID-1',
      format: 'SINGLE_CELL_EXPERIMENT',
      data: {
        SCPCP999991: {
          merge_single_cell: true,
          includes_bulk: true,
          SINGLE_CELL: [
            'SCPCS000001',
            'SCPCS000002',
            'SCPCS000003',
            'SCPCS000004'
          ],
          SPATIAL: ['SCPCS000001', 'SCPCS000005', 'SCPCS000006']
        },
        SCPCP999992: {
          merge_single_cell: true,
          includes_bulk: false,
          SINGLE_CELL: ['SCPCS000001'],
          SPATIAL: []
        },
        SCPCP999993: {
          merge_single_cell: false,
          includes_bulk: true,
          SINGLE_CELL: ['SCPCS000001', 'SCPCS000002', 'SCPCS000003'],
          SPATIAL: ['SCPCS000001', 'SCPCS000002', 'SCPCS000003', 'SCPCS000004']
        },
        SCPCP999994: {
          merge_single_cell: false,
          includes_bulk: false,
          SINGLE_CELL: ['SCPCS000002', 'SCPCS000003', 'SCPCS000004'],
          SPATIAL: []
        }
      },
      stats: {
        projects: {
          // each of the project cards here
          SCPCP999991: {
            diagnoses_counts: { 'pilocytic astrocytoma': 10, 'ganglioglioma/ATRT': 10, ganglioglioma: 9, 'low grade glioma': 1 },
            samples_difference_count: 5,
            downloadable_sample_count: 6,
            title:
              'Single-Cell Profiling of Acute Myeloid Leukemia for High-Resolution Chemo-immunotherapy Target Discovery'
          },
          SCPCP999992: {
            diagnoses_counts: { Ependymoma : 1, Ganglioglioma: 5, 'Ganglioglioma/ATRT' :1 },
            samples_difference_count: 0,
            downloadable_sample_count: 1,
            title: 'Single cell RNA sequencing of pediatric low-grade gliomas'
          },
          SCPCP999993: {
            diagnoses_counts: { Neuroblastoma: 40 },
            samples_difference_count: 1,
            downloadable_sample_count: 3,
            title:
              'Profiling the transcriptional heterogeneity of diverse pediatric solid tumors - Neuroblastoma'
          },
          SCPCP999994: {
            diagnoses_counts: { Osteosarcoma: 28 },
            samples_difference_count: 0,
            downloadable_sample_count: 3,
            title: 'A Single Cell Atlas of Pediatric Sarcoma'
          }
        }
      }
    }
  ]

export default {
  title: 'Components/DatasetProjectCard',
  args: { datasets }
}

export const Default = (args) =>  (
    <>
     {datasets.map((d) =>
        Object.keys(d.stats.projects).map((id) => (
        <Box key={d.id} width='900px'>
            <DatasetProjectCard dataset={d} projectId={id} {...args}  />
        </Box>
     ))
    )}
    </>
)

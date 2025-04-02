import React from 'react'
import 'regenerator-runtime/runtime'
import { Box} from 'grommet'
import { DatasetProjectCard } from 'components/DatasetProjectCard'

// NOTE: Mock data ("data" data structure copied from the current BE test)
const datasets = [
    {
        id: 'UUID-1',
        data: {
        SCPCP999991: {
            merge_single_cell: true,
            includes_bulk: true,
            SINGLE_CELL: ['SCPCS000001', 'SCPCS000002', 'SCPCS000003', 'SCPCS000004'],
            SPATIAL: ['SCPCS000001', 'SCPCS000005', 'SCPCS000006']
        }
        },
        diagnoses_counts:
        'pilocytic astrocytoma (10), ganglioglioma/ATRT (10), ganglioglioma (9), low grade glioma (1)',
        format: 'SINGLE_CELL_EXPERIMENT',
        downloadable_sample_count: 6,
        title:
        'Single-Cell Profiling of Acute Myeloid Leukemia for High-Resolution Chemo-immunotherapy Target Discovery'
    },
    {
        id: 'UUID-2',
        data: {
        SCPCP999992: {
            merge_single_cell: true,
            includes_bulk: false,
            SINGLE_CELL: ['SCPCS000001', 'SCPCS000002'],
            SPATIAL: []
        }
        },
        diagnoses_counts:
        'Ependymoma (1), Ganglioglioma (5), Ganglioglioma/ATRT (1)',
        format: 'ANN_DATA',
        downloadable_sample_count: 2,
        title:
        'Single cell RNA sequencing of pediatric low-grade gliomas'
    },
    {
        id: 'UUID-3',
        data: {
        SCPCP999992: {
            merge_single_cell: false,
            includes_bulk: true,
            SINGLE_CELL: ['SCPCS000001', 'SCPCS000002', 'SCPCS000003'],
            SPATIAL: ['SCPCS000001', 'SCPCS000002', 'SCPCS000003',  'SCPCS000004']
        }
        },
        diagnoses_counts: 'Neuroblastoma (40)',
        format:'SINGLE_CELL_EXPERIMENT',
        downloadable_sample_count: 3,
        title: 'Profiling the transcriptional heterogeneity of diverse pediatric solid tumors - Neuroblastoma'
    },
    {
        id: 'UUID-4',
        data: {
        SCPCP999993: {
            merge_single_cell: false,
            includes_bulk: false,
            SINGLE_CELL: ['SCPCS000002', 'SCPCS000003', 'SCPCS000004'],
            SPATIAL: []
        }
        },
        diagnoses_counts: 'Osteosarcoma (28)',
        format: 'ANN_DATA',
        downloadable_sample_count: 3,
        title: 'A Single Cell Atlas of Pediatric Sarcoma'
    }
]

export default {
  title: 'Components/DatasetProjectCard',
  args: { datasets }
}

export const Default = (args) =>  (
    <>
     {datasets.map((dataset)=> (
        <Box key={dataset.id} width='900px'>
            <DatasetProjectCard dataset={dataset} {...args}  />
        </Box>
     ))}
    </>
)

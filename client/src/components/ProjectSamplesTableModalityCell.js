import React, { useEffect, useState } from 'react'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { CheckBox } from 'components/CheckBox'

export const ProjectSamplesTableModalityCell = ({
  project,
  modality,
  samples,
  sample,
  onClick
}) => {
  const { myDataset, getDatasetProjectData, getProjectSingleCellSamples } =
    useMyDataset()
  const {
    canAdd,
    readOnly,
    allSamples,
    selectedSamples,
    selectModalitySamplesByIds
  } = useProjectSamplesTable()

  const [isAlreadyInMyDataset, setIsAlreadyInMyDataset] = useState(false)

  const isDisabled = !sample[`has_${modality.toLowerCase()}_data`]

  const datasetData = getDatasetProjectData(project)

  // Preselect samples that are already in myDataset
  useEffect(() => {
    const { SINGLE_CELL: singleCellSamples, SPATIAL: spatialSamples } =
      datasetData

    if (singleCellSamples) {
      // If the project is a merged object, add all SINGLE_CELL samples
      const samplesToSelect =
        singleCellSamples === 'MERGED'
          ? allSamples
              .filter((s) => s.has_single_cell_data)
              .map((s) => s.scpca_id)
          : singleCellSamples

      selectModalitySamplesByIds('SINGLE_CELL', samplesToSelect)
    }

    if (spatialSamples) {
      selectModalitySamplesByIds('SPATIAL', spatialSamples)
    }
  }, [myDataset, allSamples])

  // Exclude toggling already added samples in the project samples table
  useEffect(() => {
    if (!readOnly && canAdd) {
      const datasetSamplesByModality = {
        SINGLE_CELL:
          datasetData.SINGLE_CELL === 'MERGED'
            ? getProjectSingleCellSamples(samples)
            : datasetData.SINGLE_CELL || [],
        SPATIAL: datasetData.SPATIAL || []
      }

      setIsAlreadyInMyDataset(
        datasetSamplesByModality[modality].includes(sample.scpca_id)
      )
    }
  }, [myDataset, samples])

  return (
    <CheckBox
      name={modality}
      checked={
        !isDisabled
          ? selectedSamples[modality].includes(sample.scpca_id)
          : false
      }
      disabled={isDisabled || readOnly || isAlreadyInMyDataset}
      onClick={onClick}
    />
  )
}

export default ProjectSamplesTableModalityCell

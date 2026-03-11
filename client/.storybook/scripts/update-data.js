// Repopulate project and projects mock data for storybook stories
// Data should be repopulated once, each time storybook is booted up
import { writeFile } from 'node:fs/promises'
import path from 'node:path'
import { request } from './../../src/helpers/request.js'

// These projects represent the permutations of all projects. They were chosen as follows:
//    - SCPCP000001: This project has single cell sce and anndata, along with bulk
//    - SCPCP000004: This project has single cell sce and anndata, with no bulk
//    - SCPCP000006: This project has spatial data
//    - SCPCP000009: This project has multiplexed data
const projectIds = ['SCPCP000001', 'SCPCP000004', 'SCPCP000006', 'SCPCP000009']

const host = process.env.API_HOST
const version = process.env.API_VERSION
const base = `${host}/${version}/`

const getProject = async projectId => {
  const endpoint = `projects/${projectId}`
  const url = new URL(endpoint, base)

  const projectRequest = await request(url)
  if (!projectRequest.isOk) {
    console.error(`update-data: Failed to get project ${projectId} from api`)
    console.error(projectRequest.error)
    process.exit(1)
  }

  return projectRequest.response
}

const writeJSON = async (fileName, data) => {
  try {
    const filePath = path.resolve(`./.storybook/data/${fileName}`)
    await writeFile(filePath, JSON.stringify(data, null, 2).trim())
  } catch (error) {
    console.error(`An error occurred when trying to write ${fileName}: `, error)
    process.exit(1)
  }
}

// Build project.json
const project = await getProject(projectIds[0])
await writeJSON('project.json', project)

// Build projects.json
const lastProjects = await Promise.all(projectIds.slice(1).map(projectId => getProject(projectId)))
const projects = [project, ...lastProjects]
await writeJSON('projects.json', projects)

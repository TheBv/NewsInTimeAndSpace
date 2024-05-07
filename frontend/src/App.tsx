import './App.css'
import { Controller, useForm } from 'react-hook-form'
import { DatePickerElement } from 'react-hook-form-mui/date-pickers'
import { AdapterLuxon } from '@mui/x-date-pickers/AdapterLuxon'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AppBar, Autocomplete, Box, Button, Card, CardContent, CardHeader, Container, FormLabel, Grid, Modal, Paper, Slider, Tab, Tabs, TextField, Toolbar, Typography } from '@mui/material'
import { useActors } from './hooks/useActors'
import { useTypes } from './hooks/useTypes'
import { useState } from 'react'
import { APIEvent, APIGroupResponse, QueryParams, getCities, getCountries, getEvents, getRegions } from './lib/api'
import { DateTime } from 'luxon'
import { DataGrid } from '@mui/x-data-grid'



interface InternalQueryParams {
  actor: string[],
  type: string[],
  tone: number[],
  goldsteinScale: number[],
  startTime: DateTime,
  endTime: DateTime,
  radius: number,
  latitude: number,
  longitude: number,
}

function App() {
  const types = useTypes()
  const actors = useActors()

  const { control, handleSubmit } = useForm<InternalQueryParams>({
    defaultValues: {
      tone: [-10, 10],
      goldsteinScale: [-10, 10]
    }
  })

  const [tabValue, setTabValue] = useState(0);

  const [regionData, setRegionData] = useState<APIGroupResponse[]>([])
  const [cityData, setCityData] = useState<APIGroupResponse[]>([])
  const [countryData, setCountryData] = useState<APIGroupResponse[]>([])

  const [popped, setPopped] = useState(false);
  const [eventData, setEventData] = useState<APIEvent[]>([])

  const [loading, setLoading] = useState(false)
  const [loadingEvent, setLoadingEvent] = useState(false)

  const getEventData = async (group: APIGroupResponse) => {
    setLoadingEvent(true)
    setEventData(await getEvents(group.Events.slice(0, 200).map(e => e.GLOBALEVENTID)))
    setLoadingEvent(false)
  }
  console.log(eventData)
  const onSubmit = async (data: Partial<InternalQueryParams>) => {
    const queryParams: Partial<QueryParams> = {
      actor: data.actor,
      type: data.type,
      ToneMax: data.tone ? data.tone[1] : undefined,
      ToneMin: data.tone ? data.tone[0] : undefined,
      GoldsteinScaleHigh: data.goldsteinScale ? data.goldsteinScale[1] : undefined,
      GoldsteinScaleLow: data.goldsteinScale ? data.goldsteinScale[0] : undefined,
      startTime: data.startTime?.toFormat('yyyy-MM-dd'),
      endTime: data.endTime?.toFormat('yyyy-MM-dd')
    }
    setLoading(true)
    const regions = getRegions(queryParams)
    const cities = getCities(queryParams)
    const countries = getCountries(queryParams)
    setRegionData(await regions)
    setCityData(await cities)
    setCountryData(await countries)
    setLoading(false)
    console.log(queryParams)
  }
  return (
    <Container maxWidth={'xl'}>
      <LocalizationProvider dateAdapter={AdapterLuxon}>
        <AppBar position='static'>
          <Toolbar>
          <Typography variant='h6'>News In Time And Space</Typography>  
          </Toolbar>
        </AppBar>
        <Paper style={{ padding: '30px' }}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <DatePickerElement inputProps={{ fullWidth: true }} name='startTime' control={control} label='Start Time' />
              </Grid>
              <Grid item xs={6}>
                <DatePickerElement inputProps={{ fullWidth: true }} name='endTime' control={control} label='End Time' />
              </Grid>
              <Grid item xs={6}>
                <Controller
                  name='actor'
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      multiple
                      options={actors.sort((a, b) => a.Actor.localeCompare(b.Actor))}
                      value={field.value?.map(e => actors.find(t => t.Actor === e))}
                      onChange={(_e, data) => field.onChange(data.map(e => e?.Actor))}
                      getOptionLabel={(option) => option!.Actor}
                      groupBy={(option) => option ? option.Actor[0].toUpperCase() : ''}
                      renderInput={(params) => <TextField {...params} label='Actor' />}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={6}>
                <Controller
                  name='type'
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      multiple
                      options={types.sort((a, b) => a.BaseType_Name.localeCompare(b.BaseType_Name))}
                      value={field.value?.map(e => types.find(t => t.Type === e))}
                      onChange={(_e, data) => field.onChange(data.map(e => e?.Type))}
                      getOptionLabel={(option) => option!.Type_Name}
                      groupBy={(option) => option ? option.BaseType_Name : ''}
                      renderInput={(params) => <TextField {...params} label='Type' />}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name='tone'
                  control={control}
                  render={({ field }) => (
                    <div>
                      <FormLabel>Tone</FormLabel>
                      <Slider
                        {...field}
                        valueLabelDisplay='auto'
                        min={-10}
                        max={10}
                        defaultValue={[-10, 10]}
                        onChange={(_, value) => field.onChange(value)}

                      />
                    </div>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name='goldsteinScale'
                  control={control}
                  render={({ field }) => (
                    <div>
                      <FormLabel>GoldsteinScale</FormLabel>
                      <Slider
                        {...field}
                        valueLabelDisplay='auto'
                        min={-10}
                        max={10}
                        defaultValue={[-10, 10]}
                        onChange={(_, value) => field.onChange(value)}

                      />
                    </div>
                  )}
                />
              </Grid>
              <Grid item xs={12} style={{ textAlign: 'right' }}>
                <Button type='submit' variant='contained'>Submit</Button>
              </Grid>
            </Grid>
            <Tabs value={tabValue} onChange={(_e, value) => setTabValue(value)}>
              <Tab label='Country' />
              <Tab label='Region' />
              <Tab label='City' />
            </Tabs>
            <Box style={{ height: 400, width: '100%' }}>
              <DataGrid
                columns={
                  [
                    { field: 'Count', headerName: 'Count', width: 100 },
                    { field: 'Country', headerName: 'Country', width: 150 },
                    { field: 'Region', headerName: 'Region', width: 150 },
                    { field: 'City', headerName: 'City', width: 150 },
                    //{ field: 'Location', headerName: 'Location', width: 150 },
                  ]
                }
                rows={tabValue === 0 ? countryData : tabValue === 1 ? regionData : cityData}
                getRowId={(row) => row.Group_ID.toString()}
                pageSizeOptions={[5, 10, 25, 50]}
                onRowDoubleClick={(row) => { setPopped(true); getEventData(row.row) }}
                loading={loading}
              />
            </Box>
          </form>
        </Paper>
        <Modal open={popped} onClose={() => setPopped(false)}>
          <Card style={{ height: '50vh', position: 'absolute', top: '35%', left: '50%', transform: 'translate(-50%, -50%)' }}>
            <CardHeader title='Events' />
            <CardContent style={{height: '80%'}}>
            <DataGrid
              columns={
                [
                  { field: 'Location_Name', headerName: 'Location Name', width: 150 },
                  { field: 'Title', headerName: 'Title', width: 450 },
                  { field: 'Source', headerName: 'Source', width: 450, renderCell: (params) => <a href={params.value} target='_blank'>{params.value}</a> },
                  { field: 'GoldsteinScale', headerName: 'Goldstein Scale', width: 100 },
                  { field: 'AvgTone', headerName: 'Average Tone', width: 100 },
                  { field: 'Date', headerName: 'Date', width: 150 },
                ]
              }
              rows={eventData}
              loading={loadingEvent}
              getRowId={(row) => row.GLOBALEVENTID.toString()}
            />
            </CardContent>
          </Card>
        </Modal>
      </LocalizationProvider>
    </Container >
  )
}


export default App

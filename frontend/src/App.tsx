import { ChakraProvider, Grid, GridItem, Box, Image, Text, Heading, Input, Button, useToast, List, ListItem, VStack, HStack } from '@chakra-ui/react'
import { useEffect, useState, useRef } from 'react'
import axios from 'axios'

interface Member {
  id: number
  name: string
  position: string
  birthdate: string
  image: string
  description: string
}


function App() {
  const [members, setMembers] = useState<Member[]>([])
  const [inputs, setInputs] = useState<{ [key: number]: string }>({})
  const [responses, setResponses] = useState<{ [key: number]: string }>({})
  const [loading, setLoading] = useState<{ [key: number]: boolean }>({})
  const [dynamicInput, setDynamicInput] = useState('')
  const [isDynamicLoading, setIsDynamicLoading] = useState(false)
  const [showDynamic, setShowDynamic] = useState(false)
  const toast = useToast()

  useEffect(() => {
    // Fetch members
    axios.get('http://localhost:8000/api/members')
      .then(res => setMembers(res.data))
      .catch(error => console.error('Error fetching members:', error))
  }, [])

  const handleSubmit = async (memberId: number) => {
    setLoading(prev => ({ ...prev, [memberId]: true }))
    try {
      const response = await axios.post('http://localhost:8000/api/LLM_query', {
        member: memberId,
        prompt: inputs[memberId] || ''
      })
      
      setResponses(prev => ({
        ...prev,
        [memberId]: response.data
      }))
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to get response',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(prev => ({ ...prev, [memberId]: false }))
    }
  }

  const handleDynamicSubmit = async () => {
    setIsDynamicLoading(true);
    try {
      // Fetch code from LLM via API calls
      const { data: componentCode } = await axios.post(
        'http://localhost:8000/api/webpage-generation', {
          prompt: dynamicInput || ''
        }
      );

      console.log(componentCode);  // For debug purposes

      // Opens generated page in a new tab
      const blob = new Blob([componentCode], { type: 'text/html' });
      const blobUrl = URL.createObjectURL(blob);
      const newTab = window.open(blobUrl, '_blank');

      if (newTab) {
        newTab.onload = () => URL.revokeObjectURL(blobUrl);
      } else {
        URL.revokeObjectURL(blobUrl);
      }  

    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to generate content',
        status: 'error'
      });
      console.log(error);
    } finally {
      setIsDynamicLoading(false);
    }
  };


  return (
    <ChakraProvider>
      <Box p={8} bg="purple.50" minH="100vh">
        <Heading mb={8} textAlign="center" color="purple.600">
          (G)I-DLE
        </Heading>
        
        <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
          {members.map(member => (
            <Box 
              key={member.id} 
              p={6} 
              shadow="md" 
              borderWidth="1px" 
              borderRadius="md" 
              bg="white"
              _hover={{ transform: 'scale(1.02)', transition: 'transform 0.2s' }}
            >
              <Image 
                src={member.image} 
                alt={member.name}
                borderRadius="md"
                mb={4}
                h="300px"
                w="100%"
                objectFit="cover"
                fallbackSrc="https://via.placeholder.com/300x300?text=Member+Image"
              />
              <Heading fontSize="xl" mb={2}>{member.name}</Heading>
              <Text fontWeight="bold" color="purple.500">{member.position}</Text>
              <Text mt={2}>{member.description}</Text>
              <Text mt={2} fontSize="sm" color="gray.600">
                Birthdate: {member.birthdate}
              </Text>

              <Input
                mt={4}
                placeholder={`Ask about ${member.name}...`}
                value={inputs[member.id] || ''}
                onChange={(e) => setInputs(prev => ({
                  ...prev,
                  [member.id]: e.target.value
                }))}
              />
              <Button
                mt={2}
                colorScheme="purple"
                w="100%"
                isLoading={loading[member.id]}
                onClick={() => handleSubmit(member.id)}
              >
                Submit
              </Button>

              <Box mt={4} minH="100px" p={2} bg="gray.50" borderRadius="md">
                <Text whiteSpace="pre-wrap">
                  {responses[member.id] || 'Response will appear here...'}
                </Text>
              </Box>
            </Box>
          ))}
        </Grid>

        <Box mb={8} p={6} bg="white" borderRadius="md" boxShadow="md" mt={8}>
          <Heading size="lg" mb={4} color="purple.600">What do you want to read about?</Heading>
          
          {/* Dynamic Webpage Generation Input */}
          <Input
            value={dynamicInput}
            onChange={(e) => setDynamicInput(e.target.value)}
            placeholder="Tell me what you want to see about (G)I-DLE and I'll show it to you..."
            mb={4}
          />
          <Button
            colorScheme="purple"
            onClick={() => {
              setShowDynamic(true)
              handleDynamicSubmit()
            }}
            isLoading={isDynamicLoading}
            loadingText="Generating..."
          >
            Explore
          </Button>
          
        </Box>
      </Box>
    </ChakraProvider>
  )
}

export default App
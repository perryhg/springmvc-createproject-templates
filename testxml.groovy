import groovy.xml.*

def runtest()
{
	//def x = new XmlParser().parseText(fileName)
	//def x = new XmlParser().parse("descriptor4.xml")
	def x = new XmlSlurper().parse("descriptor4.xml")
	def descriptors = x.'**'.findAll{
		it.name() == 'descriptor'
	}
	
	descriptors.each{
		String desctrim = it.description.text().trim()
		it.description = desctrim
	}
	
	//println XmlUtil.serialize(descriptors)
	println XmlUtil.serialize(x)
}

def runtest1()
{
	def input = '''
              <shopping>
                  <category version="1.0">
                      <item>Pen</item>
                      <color>Red</color>
                  </category>
              <category>
                      <item>Pencil</item>
                      <color>Black</color>
                  </category>
                  <category>
                      <item>Paper</item>
                      <color>White</color>
                  </category>
              </shopping>
    '''
	
	def root = new XmlSlurper().parseText(input)
	def supplies = root.category.find{ it.item == 'Pen' }
	supplies.color = 'Changed'
	supplies.@version = '2.0'
	
	println XmlUtil.serialize(root)
}

def runtest2()
{
	//def x = new XmlParser().parseText(fileName)
	//def x = new XmlParser().parse("descriptor4.xml")
	String fileName = 'template.xml'
	File xmlFile = new File(fileName)
	def x = new XmlSlurper().parse(fileName)
	def descriptor = x.'**'.find{
		println it.name()
		it.@id == 'springmvc41.template'
	}
	
	descriptor.@version = '2.2.2'
	
	println XmlUtil.serialize(descriptor)
	//println XmlUtil.serialize(x)
}

runtest2()
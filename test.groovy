import java.nio.file.*
import java.util.zip.*
import groovy.xml.*
import groovy.transform.Field

//import fileserver

//fs = new fileserver()
//fs.startServer()
//tmplutil = new templateutil()
//tmplutil.updateVersion("1.0.5")
//tmplutil.repackTmpl()
//tmplutil.repackTmplWithDesc()
//tmplutil.updateSize()
//tmplutil.extractTemplate()

versionStr = "1.1.4"
writeVersionDesc(versionStr, 'desc4.xml')

void writeVersionDesc(versionStr, fileName)
{
	//String fileName = 'descriptor4.xml'
	File xmlFile = new File(fileName)
	//def x = new XmlParser().parseText(xmlFile.text)
	def x = new XmlSlurper().parse(xmlFile)
	def result = x.'**'.find{ it.@id=="springmvc41.template" }
	//println result.@size
	//println result.@version
	//result.@version = "1.0.6"
	result.@version=versionStr
	//String xmlDesc = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
	def dList = x.descriptor.description;
	println dList.size()
	dList.each{
		//println '--------'
		//println it.getClass().getName()
		//println it.name()
		//println it.text()
		//println it
		def trimmedText = it.text().trim();
		//println trimmedText
		it.replaceBody(trimmedText)
	}
	String xmlstr = buildXml(x)
	def writer = xmlFile.newWriter()
	//writer << xmlDesc
	writer << xmlstr
	writer.close()
}

String buildXml(node)
{
	//def writer = new StringWriter()
	//new XmlNodePrinter(new PrintWriter(writer)).print(node)
	//def result1 = writer.toString()
	
	//return result1

	return XmlUtil.serialize(node);
}
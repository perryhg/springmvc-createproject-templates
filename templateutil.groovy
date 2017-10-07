import java.nio.file.*
import java.util.zip.*
import groovy.xml.*
import groovy.transform.Field

@Field String zipfilename = 'springmvc4.templates.1.1.0.zip'
@Field String[] zipEntryNames = ['template.xml', 'template.zip', 'wizard.json']

void extractZipContent(inputStream, name)
{
	println "extracting $name"
	def fos= new FileOutputStream(name)
	byte b
	while((b = inputStream.read())!=-1)
	{
		fos.write(b);
	}
	fos.flush();
	fos.close();
}

void extractEntries()
{
	zipFile = new java.util.zip.ZipFile(new File(zipfilename))
	zipFile.entries().each {
	    extractZipContent(zipFile.getInputStream(it), it.name)
	}
}

void backupzip()
{
	Date d = new Date()
	String suffix = d.format("yyMMdd'T'hhmmss")
	def filenamenew = "${zipfilename}.${suffix}.zip"
	println filenamenew

	println "backup..."
	new File(filenamenew).bytes = new File(zipfilename).bytes
	Files.delete(Paths.get(zipfilename))
}

void putEntry(file, zipFile)
{
	zipFile.putNextEntry(new ZipEntry(file.getName()))  
	def buffer = new byte[1024]  
	file.withInputStream { inputStream ->
		// println i.getClass().getName()
		// int l =0
		// while((l = i.read(buffer) > 0))
		// {
		// 	zipFile.write(buffer, 0, l)  
		// }
		byte b
		while((b = inputStream.read())!=-1)
		{
			zipFile.write(b);
		}
	}
	zipFile.closeEntry()
}

void extractTemplate(){
	String tmpFilename = "template.zip"
	def ant = new AntBuilder()
	ant.unzip(src:tmpFilename, dest:".")
}

void repackTmpl()
{
	String tmpFilename = "template.zip"
	Files.deleteIfExists(Paths.get(tmpFilename))
	File excludesfile = new File('excludesfile.txt')
	def exclWriter = excludesfile.newWriter()

	File f = new File(".")
	f.eachFile(){
		//println it
		if(it.isFile())
		{
			exclWriter<<it.name<<'\n'
		}
		else if(it.name!="template")
		{
			exclWriter<<"${it.name}/**"<<'\n'
		}
	}
	exclWriter.close()

	def ant = new AntBuilder()
	ant.zip(
		destfile: "template.zip",
		basedir:".",
		excludesfile:excludesfile.name,
		update:"false"
	)

	Files.deleteIfExists(Paths.get(excludesfile.name))
}

void repackTmplWithDesc()
{
	ZipOutputStream zipFile = new ZipOutputStream(new FileOutputStream(zipfilename))
	
	zipEntryNames.each{
		//println "storing ${it}"
		putEntry(new File(it), zipFile)
	}
	zipFile.close()
}

void readVersionDesc()
{
	String fileName = 'descriptor4.xml'
	def x = new XmlParser().parseText(new File(fileName).text)
	def result = x.find{ it.@id=="springmvc41.template" }
	println result.@size
	println result.@version
}

String readVersionTmpl()
{
	String fileName = 'template.xml'
	def x = new XmlParser().parseText(new File(fileName).text)
	def result = x.find{ it.@id=="springmvc41.template" }
	return result.@version
}

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

void writeVersionTmpl(versionStr)
{
	String fileName = 'template.xml'
	File xmlFile = new File(fileName)
	//def x = new XmlParser().parseText(xmlFile.text)
	def x = new XmlSlurper().parse(xmlFile)
	
	def result = x.'**'.find{
		println it.name
		it.@id=="springmvc41.template"
	}
	//println result.@version
	result.@version=versionStr
	String xmlstr = trimxml(buildXml(x))

	def writer = xmlFile.newWriter()
	writer << xmlstr
	writer.close()
}

String trimxml(strsrc)
{
	println strsrc
	return strsrc
}

String buildXml(node)
{
	return XmlUtil.serialize(node);
}

void updateVersion(String versionStr)
{
	writeVersionTmpl(versionStr)
	writeVersionDesc(versionStr, 'descriptor4.xml')
	writeVersionDesc(versionStr, 'desc4.xml')
}

void updateSizeDesc(sizeStr, fileName)
{
	//String fileName = 'descriptor4.xml'
	File xmlFile = new File(fileName)
	def x = new XmlParser().parseText(xmlFile.text)
	def result = x.find{ it.@id=="springmvc41.template" }
	//println result.@size
	//println result.@version
	//result.@version = "1.0.6"
	result.@size=sizeStr
	String xmlDesc = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
	String xmlstr = buildXml(x)
	def writer = xmlFile.newWriter()
	//writer << xmlDesc
	writer << xmlstr
	writer.close()
}

void updateSize()
{
	File zipTFile = new File(zipfilename)
	String sizeStr = String.valueOf( zipTFile.size() )
	updateSizeDesc(sizeStr, 'descriptor4.xml')
	updateSizeDesc(sizeStr, 'desc4.xml')
}

// String ver = readVersionTmpl()
// println ver
//extractEntries()
//repack()
//readVersionDesc()
//writeVersionTmpl()
//writeVersionDesc()
//tmplutil.updateVersion("1.0.5")
//tmplutil.repackTmpl()
//tmplutil.repackTmplWithDesc()
//tmplutil.updateSize()

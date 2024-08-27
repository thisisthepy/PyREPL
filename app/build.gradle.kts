import org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi
import org.jetbrains.kotlin.gradle.plugin.KotlinSourceSet
import org.jetbrains.kotlin.gradle.dsl.kotlinExtension
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.objectweb.asm.tree.MethodNode
import org.objectweb.asm.tree.FieldNode
import org.objectweb.asm.tree.ClassNode
import org.objectweb.asm.ClassReader
import org.objectweb.asm.Opcodes
import com.google.gson.Gson
import java.util.jar.JarFile
import java.nio.file.Paths
import java.nio.file.Path


plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.compose)
    alias(libs.plugins.compose.compiler)
    alias(libs.plugins.chaquo.python)
}


group = "io.github.thisisthepy.pythonapptemplate"
version = "1.0.0.0"


kotlin {
    androidTarget {
        @OptIn(ExperimentalKotlinGradlePluginApi::class)
        compilerOptions {
            jvmTarget.set(JvmTarget.JVM_11)
        }
    }
    
    sourceSets {
        androidMain.dependencies {
            api(projects.pycomposeui)
        }

        commonMain.dependencies {
            api(projects.pycomposeui)
        }
    }
}


chaquopy {
    defaultConfig {
        version = libs.versions.python.get()

        pyc {
            src = false
            pip = false
        }

        pip {
            // Use the local repository for the Python packages.
            options("--extra-index-url", "libs/pip/local")
            install("pip")
            install("setuptools ")

            // Dependencies for the llama-cpp-python package.
            install("typing-extensions")
            install("numpy")
            install("diskcache")
            install("jinja2")
            install("MarkupSafe")
            install("llama-cpp-python")

            // Dependencies for the huggingface_hub package.
            install("PyYAML")
            install("huggingface_hub")

            // Dependencies for the jupyter package.
            install("pyzmq")
            install("rpds-py")
            install("argon2-cffi-bindings")
            install("jupyterlab==4.2.4")
            install("jupyterthemes")
            install("jupyter")
        }
    }

    sourceSets {
        getByName("main") {
            srcDirs(
                "src/androidMain/python", "src/androidMain/generated/meta",
                "src/commonMain/python", "src/commonMain/generated/meta"
            )
        }
    }
}


android {
    namespace = group.toString()
    compileSdk = libs.versions.android.compileSdk.get().toInt()

    sourceSets["main"].manifest.srcFile("src/androidMain/AndroidManifest.xml")
    sourceSets["main"].res.srcDirs("src/androidMain/res")
    sourceSets["main"].resources.srcDirs("src/commonMain/resources")

    defaultConfig {
        applicationId = group.toString()
        minSdk = libs.versions.android.minSdk.get().toInt()
        targetSdk = libs.versions.android.targetSdk.get().toInt()
        versionCode = 1
        versionName = version.toString()
        ndk {
            abiFilters += listOf("arm64-v8a", "x86_64", "armeabi-v7a", "x86")
        }
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
    }
    dependencies {
        debugImplementation(compose.uiTooling)
    }
}


val createKotlinMetaPackageForPython by tasks.registering {
    val (dependencyTree, unresolvedTree, isChanged) = project.resolveDependenciesForPython()
    outputs.upToDateWhen {
        false//!isChanged
    }
    doLast {
        //if (!isChanged) return@doLast  // Skip if the meta_json.lock file is not changed

        // Print dependency tree
        dependencyTree.forEach { (sourceSet, dependencies) ->
            println("Dependencies for source set: ${sourceSet.name}")
            println("  Meta package generation directory: ${dependencies.first}")
            val unresolvedDependencies = unresolvedTree[sourceSet] ?: emptyMap()

            dependencies.second.forEach { (type, artifacts) ->
                val unresolved = unresolvedDependencies[type] ?: emptyList()

                println("  Configuration: ${sourceSet.name}$type")
                println("    Resolved artifacts:" + if (artifacts.isNotEmpty()) "" else " NONE")
                artifacts.forEach { artifact ->
                    println("      ${artifact.file.absolutePath}")
                }
                println("    Unresolved dependencies:" + if (unresolved.isNotEmpty()) "" else " NONE")
                unresolved.forEach { unresolvedDependency ->
                    println("      ${unresolvedDependency.selector}")
                    val message = unresolvedDependency.problem.message.toString()
                        .replace("    project", "            project")
                        .replace("Required by:", "          Required by:")
                    println("        - Problem: $message")
                }
            }
        }

        val classPathList = mutableSetOf<File>()

        // Create meta package
        print("\nAssembling meta package for Kotlin source sets...")
        System.out.flush()
        dependencyTree.forEach { (_, dep) ->
            val artifacts = dep.second[DependencyType.IMPLEMENTATION]!! + dep.second[DependencyType.API]!!
            if (artifacts.isEmpty()) return@forEach  // Skip if there are no artifacts
            val metaPackageDir = File(dep.first.toString())
            if (metaPackageDir.exists()) {
                metaPackageDir.deleteRecursively()  // Clean the directory
            }
            metaPackageDir.mkdirs()  // Create the directory
            classPathList.add(metaPackageDir)
            artifacts.forEach {
                processJarForMetaPackage(it.file.absolutePath, metaPackageDir)  // Process lib files
//                println(it.file.absolutePath)
            }
        }

        checkForOverlappingClass(classPathList)

        println(" Done!")
    }
}

project.tasks.getByName("prepareKotlinIdeaImport").dependsOn(createKotlinMetaPackageForPython)


enum class DependencyType(private val type: String) {
    IMPLEMENTATION("Implementation"), API("Api");

    override fun toString(): String {
        return type
    }
}


fun Project.resolveDependenciesForPython(isSubModule: Boolean = false, sourceSetName: String? = null)
        : Triple<
        MutableMap<KotlinSourceSet, Pair<Path, MutableMap<DependencyType, List<ResolvedArtifact>>>>,
        MutableMap<KotlinSourceSet, MutableMap<DependencyType, List<UnresolvedDependency>>>,
        Boolean>
{
    val dependencyTree = mutableMapOf<KotlinSourceSet, Pair<Path, MutableMap<DependencyType, List<ResolvedArtifact>>>>()
    val unresolvedTree = mutableMapOf<KotlinSourceSet, MutableMap<DependencyType, List<UnresolvedDependency>>>()
    var isMetaJsonLockFileChanged = false

    // Build a dependency tree
    this.kotlinExtension.sourceSets.forEach { sourceSet ->
        // Skip source set if sourceSetName is not null and does not match to the requested source set
        if (sourceSetName != null && sourceSet.name != sourceSetName) return@forEach

        val sourceSetDependencyTree = mutableMapOf<DependencyType, List<ResolvedArtifact>>()
        val sourceSetUnresolvedTree = mutableMapOf<DependencyType, List<UnresolvedDependency>>()

        // default source set
        val srcNameWithDefaults = sourceSet.kotlin.srcDirs.mapNotNull {
            if (it.toString().contains(Paths.get(sourceSet.name, "kotlin").toString())) it else null
        }
        // custom named source set (kotlin, java)
        val srcNameWithCustom = sourceSet.kotlin.srcDirs.mapNotNull {
            if (it.toString().endsWith(Paths.get("", "kotlin").toString())
                || it.toString().endsWith(Paths.get("", "java").toString())) it else null
        }
        val targetDir = srcNameWithDefaults.firstOrNull() ?: srcNameWithCustom.firstOrNull() ?: sourceSet.kotlin.srcDirs.first()
        val generationDir = Paths.get(targetDir.parent!!, "generated", "meta")

        dependencyTree[sourceSet] = Pair(generationDir, sourceSetDependencyTree)
        unresolvedTree[sourceSet] = sourceSetUnresolvedTree

        when (isSubModule) {
            false -> mapOf(
                DependencyType.IMPLEMENTATION to configurations.getByName(sourceSet.implementationConfigurationName),
                DependencyType.API to configurations.getByName(sourceSet.apiConfigurationName)
            )
            true -> mapOf(  // when the project is a submodule
                DependencyType.API to configurations.getByName(sourceSet.apiConfigurationName)
            )
        }.forEach { (dependencyType, configuration) ->
            // Making configuration copy with isCanBeResolved = true
            val resolved = try {
                configurations.create(configuration.name + "Resolved") {
                    extendsFrom(configuration)
                    isCanBeResolved = true
                }
            } catch (ignored: Exception) { configurations.getByName(configuration.name + "Resolved") }
            val lenientConfiguration = resolved.resolvedConfiguration.lenientConfiguration

            // Adding dependencies to the tree
            val artifacts = lenientConfiguration.artifacts.toMutableList()
            sourceSetDependencyTree[dependencyType] = artifacts
            val unresolved = mutableListOf<UnresolvedDependency>()
            sourceSetUnresolvedTree[dependencyType] = unresolved

            // Handling unresolved dependencies
            lenientConfiguration.unresolvedModuleDependencies.forEach { unresolvedDependency ->
                if (
                    unresolvedDependency.problem.message?.contains(
                        "project :${unresolvedDependency.selector.name}"
                    ) == true
                ) {
                    val (submoduleDependency, raised, _) = project(":"+unresolvedDependency.selector.name)
                        .resolveDependenciesForPython(isSubModule = true, sourceSetName = sourceSet.name)
                    submoduleDependency.forEach { (key, value) ->
                        if (key.name == sourceSet.name) { artifacts.addAll(value.second[DependencyType.API]!!) }
                    }
                    raised.forEach { (key, value) ->
                        if (key.name == sourceSet.name) { unresolved.addAll(value[DependencyType.API]!!) }
                    }
                } else {
                    unresolved.add(unresolvedDependency)
                }
            }
        }
    }

    if (!isSubModule) {
        val gson = Gson()
        val metaJsonDir = File(project.projectDir, Paths.get( "build", "kotlin-python").toString())
        metaJsonDir.mkdirs()
        val metaJsonLockFile = File(metaJsonDir, "meta_json.lock")
        val metaJsonNewFile = File(metaJsonDir, "meta_json.new")
        metaJsonLockFile.createNewFile()
        metaJsonNewFile.createNewFile()

        // Create build/kotlin-python/meta_json.new file
        metaJsonNewFile.writeText(gson.toJson(dependencyTree.map {
            it.key to mapOf(
                "directory" to it.value.first.toString(),
                "artifacts" to it.value.second.map { (type, artifacts) ->
                    type.toString() to artifacts.map { artifact ->
                        mapOf(
                            "name" to artifact.name,
                            "group" to artifact.moduleVersion.id.group,
                            "version" to artifact.moduleVersion.id.version,
                            "file" to artifact.file.absolutePath
                        )
                    }
                }.toMap()
            )
        }.associate { (sourceSet, dependencies) ->
            sourceSet.name to dependencies
        }))
        val metaJsonNew = gson.fromJson(metaJsonNewFile.readText(), Map::class.java)

        // Compare artifacts with build/kotlin-python/meta_json.lock
        if (metaJsonLockFile.exists()) {
            val metaJsonLock = gson.fromJson(metaJsonLockFile.readText(), Map::class.java)
            if (metaJsonLock != metaJsonNew) {
                isMetaJsonLockFileChanged = true

                // Replace build/kotlin-python/meta_json.lock with .new
                metaJsonLockFile.writeText(gson.toJson(metaJsonNew))
            }
        }
        metaJsonNewFile.delete()
    }
    return Triple(dependencyTree, unresolvedTree, isMetaJsonLockFileChanged)
}


fun processJarForMetaPackage(jarPath: String, outputDir: File) {
    JarFile(jarPath).use { jar ->
        val classNodes = mutableMapOf<String, ClassNode>()

        // First, read all classes from the JAR
        jar.entries().asSequence()
            .filter { it.name.endsWith(".class") }
            .forEach { entry ->
                val classReader = ClassReader(jar.getInputStream(entry))
                val node = ClassNode()
                classReader.accept(node, ClassReader.SKIP_CODE or ClassReader.SKIP_DEBUG or ClassReader.SKIP_FRAMES)
                classNodes[node.name] = node
            }

        // Sort classes by their names
        val sortedClasses = classNodes.toSortedMap()

        // Generate Python files for each class
//        sortedClasses.values.forEach { node ->
//            val pyFile = createInitPythonFile(node, outputDir)
//            generateMetaPythonClass(node, pyFile, classNodes)
//        }

        // Then, process only top-level classes
        classNodes.values.forEach { node ->
            if (!node.name.contains('$') && !node.access.hasFlag(Opcodes.ACC_PRIVATE) && !node.access.hasFlag(Opcodes.ACC_PROTECTED)) {
                val pyFile = createInitPythonFile(node, outputDir)
                generateMetaPythonClass(node, pyFile, classNodes)
            }
        }
    }
}

fun createInitPythonFile(node: ClassNode, outputDir: File): File {
    val packagePath = node.name.substringBeforeLast('/').replace('/', File.separatorChar)
    val packageDir = File(outputDir, packagePath)
    packageDir.mkdirs()
    return File(packageDir, "__init__.pyi")
}

fun generateMetaPythonClass(node: ClassNode, pyFile: File, allClasses: Map<String, ClassNode>) {
    val className = node.name.substringAfterLast('/')
    val nestedClasses = mutableMapOf<String, ClassNode>()

    if (pyFile.length().toInt() == 0) { // If file empty
        pyFile.appendText("class $className:\n")
    } else { // If not empty
        pyFile.appendText("\nclass $className:\n")
    }

    val fields = node.fields
        .filter { !it.access.hasFlag(Opcodes.ACC_PRIVATE) && !it.access.hasFlag(Opcodes.ACC_PROTECTED) }
        .filter { !it.name.startsWith("\$") }
        .filter { !it.name.startsWith("Companion") }

    val methods = node.methods
        .filter { !it.access.hasFlag(Opcodes.ACC_PRIVATE) && !it.access.hasFlag(Opcodes.ACC_PROTECTED) }
        .filter { !it.name.startsWith("<") }

    generateMetaPythonClassFields(pyFile, fields, className)
    generateMetaPythonClassMethods(pyFile, methods)

    // Process nested classes
    node.innerClasses.forEach { innerClass ->
        if (innerClass.name.startsWith(node.name) && innerClass.name != node.name) {
            val nestedClassName = innerClass.name.substringAfterLast('$')
            allClasses[innerClass.name]?.let { nestedClassNode ->
                nestedClasses[nestedClassName] = nestedClassNode
            }
        }
    }

    // Generate nested classes
    nestedClasses.forEach { (nestedClassName, nestedClassNode) ->
        // Skip anonymous classes
        if (nestedClassName.toIntOrNull() != null) return@forEach

        pyFile.appendText("\n    class $nestedClassName:\n")

        val nestedFields = nestedClassNode.fields
            .filter { !it.access.hasFlag(Opcodes.ACC_PRIVATE) && !it.access.hasFlag(Opcodes.ACC_PROTECTED) }
            .filter { !it.name.startsWith("\$") }

        val nestedMethods = nestedClassNode.methods
            .filter { !it.access.hasFlag(Opcodes.ACC_PRIVATE) && !it.access.hasFlag(Opcodes.ACC_PROTECTED) }
            .filter { !it.name.startsWith("<") }

        generateMetaPythonClassFields(pyFile, nestedFields, "$className.$nestedClassName", "        ")
        generateMetaPythonClassMethods(pyFile, nestedMethods, "        ")

        if (nestedFields.isEmpty() && nestedMethods.isEmpty()) {
            generateMetaPythonEmptyClass(pyFile, indent = "    ")
        }
    }

    if (methods.isEmpty() && fields.isEmpty() && nestedClasses.isEmpty()) {
        generateMetaPythonEmptyClass(pyFile)
//        println("non field found in $className, ${node.name}")
    }
}


fun generateMetaPythonEmptyClass(pyFile: File, indent: String = "") {
    pyFile.appendText("$indent    ...\n")
}


fun generateMetaPythonClassFields(pyFile: File, fields: List<FieldNode>, className: String, indent: String = "    ") {
    fields.forEach { field ->
        val fieldName = field.name
        val fieldType = field.desc.toReadableType(if (className.contains(".")) {
            val index = className.indexOf('.')
            className.substring(index+1)
        } else {
            className
        })
        if (fieldName.contains("INSTANCE")) {
            pyFile.appendText("\n${indent}INSTANCE: $className\n")
        } else {
            pyFile.appendText("\n$indent$fieldName: ${fieldType.substringAfterLast('.')}\n")
        }
    }
}


fun generateMetaPythonClassMethods(pyFile: File, methods: List<MethodNode>, indent: String = "    ") {
    val methodGroups = methods.groupBy { it.name.substringBefore('$') }
    val nameSpace = mutableListOf<String>()

    methodGroups.forEach { (baseName, group) ->
//        val hasAnnotations = group.any { it.name.contains('$') }
//        val converted = baseName.convertToSnakeCase().stripeDash()  // Replace Kotlin's special characters
        val converted = baseName.removeAfterDash()
        val pythonName = converted // .convertToPythonMethodName()
//        if (nameSpace.contains(pythonName)) return@forEach
        pyFile.appendText("${indent}def $pythonName(self, *args, **kwargs): ...\n")
//        writer.write("${indent}    __meta__.${group.first().name.stripeDash()}(*args, **kwargs)\n")
        nameSpace.add(pythonName)
    }
}


fun String.removeAfterDash(): String {
    return this.substringBefore("-")
}


fun String.toReadableType(className: String): String {
    return when {
        this.startsWith("L") && this.endsWith(";") -> {
            val type = this.substring(1, this.length - 1).replace('/', '.')
            if (type.contains('$')) {
                val outerClass = type.substringBefore('$')
                val innerClass = type.substringAfter('$')
                if (outerClass == className) innerClass else type
            } else {
                type
            }
        }
        this == "I" -> "jint"
        this == "J" -> "jlong"
        this == "Z" -> "jboolean"
        this == "F" -> "jfloat"
        this == "D" -> "jdouble"
        this == "V" -> "jvoid"
        this.startsWith("[") -> this.substring(1).toReadableType(className) + "[]"
        else -> this
    }
}


fun Int.hasFlag(flag: Int): Boolean = (this and flag) != 0


fun String.stripeDash(): String = (if (this.contains("-")) this.substring(0, this.indexOf('-')) else this).trim()


fun String.convertToSnakeCase(): String = this.fold("") { acc, char ->
    if (char.isUpperCase()) {
        acc + "_" + char.lowercaseChar()
    } else {
        acc + char
    }
}.trimStart('_')


fun checkForOverlappingClass(classPathList: Set<File>) {
    val commonMainClassPath = classPathList.first { it.absolutePath.contains("commonMain") }
    val otherClassPath = classPathList.filter { !it.absolutePath.contains("commonMain") }

    val commonMainList = buildDirList(commonMainClassPath)
    val otherList = otherClassPath.map { buildDirList(it) }

    val common = mutableListOf<Triple<String, String, String>>()
    otherList.forEach {
        findCommonDir(commonMainList, it).forEach { res ->
            common.add(res)
        }
    }

    reCreateFile(common)
}

fun buildDirList(classPath: File): List<Pair<String, String>> {
    val classPathList = mutableListOf<Pair<String, String>>()
    classPath.walk().forEach { f ->
        val path = f.absolutePath.substringAfter(classPath.path)
        if (!f.isDirectory) {
            classPathList.add(Pair(classPath.path, path))
        }
    }
    return classPathList
}

fun findCommonDir(commonMainList: List<Pair<String, String>>, otherList: List<Pair<String, String>>): List<Triple<String, String, String>> {
    val common = mutableListOf<Triple<String, String, String>>()
    commonMainList.forEach { (commonDir, commonClass) ->
        otherList.forEach { (otherDir, otherClass) ->
            if (commonClass == otherClass) {
                val className = commonClass.substringBefore("\\__init__.pyi").substringAfterLast("\\")
                val commonDirN = commonDir + commonClass.substringBeforeLast("\\__init__.pyi")
                val otherDirN = otherDir + otherClass.substringBeforeLast("\\__init__.pyi")
                common.add(Triple(commonDirN, otherDirN, className))
            }
        }
    }
    return common
}

fun reCreateFile(common: List<Triple<String, String, String>>) {
    common.forEach { (commonDir, otherDir, commonClass) ->
        val commonFile = File(commonDir, "__init__.pyi")
        val otherFile = File(otherDir, "__init__.pyi")

        val otherTargetName = otherDir.substringBefore("Main\\generated\\meta").substringAfterLast("\\")

        commonFile.renameTo(File(commonDir, "_$commonClass.pyi"))
        otherFile.renameTo(File(otherDir, "_${commonClass}_$otherTargetName.pyi"))

        reCreateInitFile(commonDir, commonClass, otherTargetName)
    }
}

fun reCreateInitFile(commonDir: String, commonClass: String, otherTargetName: String) {
    val reInit = File(commonDir, "__init__.pyi")
    reInit.appendText("from ._$commonClass import *\n")
    reInit.appendText("from ._${commonClass}_$otherTargetName import *")
}


//fun String.convertToPythonMethodName(): String = when (this) {
//    "from" -> "_from_"
//    "global" -> "_global_"
//    "import" -> "_import_"
//    "lambda" -> "_lambda_"
//    "nonlocal" -> "_nonlocal_"
//    "raise" -> "_raise_"
//    "try" -> "_try_"
//    "with" -> "_with_"
//    "yield" -> "_yield_"
//
//    "to_string" -> "__str__"
//    "to_int" -> "__int__"
//    "to_float" -> "__float__"
//    "to_bool" -> "__bool__"
//    "to_bytes" -> "__bytes__"
//    "to_list" -> "__list__"
//    "to_tuple" -> "__tuple__"
//    "to_set" -> "__set__"
//    "to_frozenset" -> "__frozenset__"
//    "to_dict" -> "__dict__"
//
//    "add" -> "__add__"
//    "sub" -> "__sub__"
//    "mul" -> "__mul__"
//    "truediv" -> "__truediv__"
//    "floordiv" -> "__floordiv__"
//    "mod" -> "__mod__"
//    "pow" -> "__pow__"
//    "equal" -> "__eq__"
//    "equals" -> "__eq__"
//    "hash" -> "__hash__"
//    "hash_code" -> "__hash__"
//    "length" -> "__len__"
//    "copy" -> "__copy__"
//
//    else -> this
//}


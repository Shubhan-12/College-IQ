plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    kotlin("kapt")

    id("com.google.gms.google-services")
}

android {
    namespace = "com.example.collegeiq"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.collegeiq"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner =
            "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {

        release {

            isMinifyEnabled = false

            proguardFiles(
                getDefaultProguardFile(
                    "proguard-android-optimize.txt"
                ),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {

        sourceCompatibility =
            JavaVersion.VERSION_11

        targetCompatibility =
            JavaVersion.VERSION_11

        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {

        jvmTarget = "11"
    }

    buildFeatures {

        compose = true
    }
}

dependencies {

    implementation(libs.androidx.core.ktx)

    implementation(libs.androidx.lifecycle.runtime.ktx)

    implementation(libs.androidx.activity.compose)

    implementation(
        "androidx.compose.foundation:foundation:1.6.0"
    )

    implementation(
        platform(libs.androidx.compose.bom)
    )


    implementation(libs.androidx.compose.ui)

    implementation(
        "androidx.compose.material:material-icons-extended"
    )

    implementation(libs.androidx.compose.ui.graphics)

    implementation(
        libs.androidx.compose.ui.tooling.preview
    )

    implementation(libs.androidx.compose.material3)

    implementation(libs.androidx.compose.foundation)

    implementation(libs.androidx.navigation.runtime.ktx)

    implementation(libs.androidx.navigation.compose)

    // -----------------------------
    // Networking
    // -----------------------------
    implementation(
        "com.squareup.retrofit2:retrofit:2.9.0"
    )

    implementation(
        "com.squareup.retrofit2:converter-gson:2.9.0"
    )

    implementation(
        "com.squareup.okhttp3:okhttp:4.12.0"
    )

    // -----------------------------
    // Firebase
    // -----------------------------
    implementation(
        platform(
            "com.google.firebase:firebase-bom:33.5.1"
        )
    )

    implementation(
        "com.google.firebase:firebase-analytics"
    )

    implementation("com.google.firebase:firebase-auth")

    implementation(
        "com.google.android.gms:play-services-auth:21.2.0"
    )

    // -----------------------------
    // Gemini
    // -----------------------------
    implementation(libs.generativeai)

    // -----------------------------
    // Charts
    // -----------------------------
    implementation(
        "com.github.PhilJay:MPAndroidChart:v3.1.0"
    )

    // -----------------------------
    // Konfetti
    // -----------------------------
    implementation(
        "nl.dionsegijn:konfetti-compose:2.0.2"
    )

    // -----------------------------
    // Coroutines
    // -----------------------------
    implementation(
        "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
    )

    // -----------------------------
    // ViewModel
    // -----------------------------
    implementation(
        "androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2"
    )

    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // -----------------------------
    // Desugaring
    // -----------------------------
    coreLibraryDesugaring(
        "com.android.tools:desugar_jdk_libs:2.0.4"
    )

    // -----------------------------
    // Testing
    // -----------------------------
    testImplementation(libs.junit)

    androidTestImplementation(libs.androidx.junit)

    androidTestImplementation(
        libs.androidx.espresso.core
    )

    androidTestImplementation(
        platform(libs.androidx.compose.bom)
    )

    androidTestImplementation(
        libs.androidx.compose.ui.test.junit4
    )

    debugImplementation(
        libs.androidx.compose.ui.tooling
    )

    debugImplementation(
        libs.androidx.compose.ui.test.manifest
    )
}
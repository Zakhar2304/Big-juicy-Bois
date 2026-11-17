Pod::Spec.new do |s|
  s.name             = 'happygarden_phone'
  s.version          = '0.0.1'
  s.summary          = 'HappyGarden home screen widget bridge'
  s.homepage         = 'https://happygarden.local'
  s.license          = { :type => 'Proprietary' }
  s.author           = { 'HappyGarden' => 'hello@happygarden.local' }
  s.source           = { :path => '.' }
  s.source_files     = 'Classes/**/*'
  s.dependency 'Flutter'
  s.platform         = :ios, '15.0'
  s.frameworks       = 'WidgetKit'
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES' }
  s.swift_version    = '5.0'
end

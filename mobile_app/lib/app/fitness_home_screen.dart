import 'package:flutter/material.dart';
import '../data/repositories/fitness_models.dart';
import '../data/repositories/local_fitness_repository.dart';
const ink=Color(0xFF17211F), muted=Color(0xFF75827D), lime=Color(0xFFB8F36B), canvas=Color(0xFFF3F5F1);
class FitnessHomeScreen extends StatelessWidget {
 const FitnessHomeScreen({required this.userId,required this.email,required this.repository,super.key});
 final String userId,email; final LocalFitnessRepository repository;
 @override Widget build(BuildContext context)=>FutureBuilder<List<Object?>>(
  future:Future.wait<Object?>([repository.getProfile(userId),repository.getWorkoutLogs(userId),repository.getBodyStats(userId)]),
  builder:(context,snap){
   if(snap.connectionState!=ConnectionState.done)return const Center(child:CircularProgressIndicator());
   if(snap.hasError)return const Center(child:Text('Dashboard could not be loaded. Your saved data is safe.'));
   final profile=snap.data![0] as FitnessProfile?; final logs=snap.data![1] as List<WorkoutLog>;
   final name=profile?.displayName.trim().isNotEmpty==true?profile!.displayName.trim().split(' ').first:'Athlete';
   final now=DateTime.now(); final week=logs.where((w)=>w.workoutDate.isAfter(now.subtract(const Duration(days:7)))).length;
   final today=logs.where((w)=>w.workoutDate.year==now.year&&w.workoutDate.month==now.month&&w.workoutDate.day==now.day).length;
   return Container(color:canvas,child:ListView(padding:const EdgeInsets.fromLTRB(20,14,20,28),children:[
    Row(children:[Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
     const Text('YOUR PERSONAL SPACE',style:TextStyle(color:muted,fontSize:10,letterSpacing:1.7,fontWeight:FontWeight.w800)),
     const SizedBox(height:5),Text('Good '+_greeting()+', '+name,style:const TextStyle(color:ink,fontSize:24,height:1.12,fontWeight:FontWeight.w800)),
    ])),Container(width:46,height:46,decoration:BoxDecoration(color:ink,borderRadius:BorderRadius.circular(16)),child:const Icon(Icons.bolt_rounded,color:lime))]),
    const SizedBox(height:22),
    Container(padding:const EdgeInsets.all(20),decoration:BoxDecoration(color:ink,borderRadius:BorderRadius.circular(24),gradient:const LinearGradient(colors:[Color(0xFF263631),Color(0xFF111A17)])),
     child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
      const Text('THIS WEEK',style:TextStyle(color:Color(0xFFB8C5BE),fontSize:10,letterSpacing:1.8,fontWeight:FontWeight.w800)),
      const SizedBox(height:14),Row(crossAxisAlignment:CrossAxisAlignment.end,children:[
       Text('$week',style:const TextStyle(color:Colors.white,fontSize:48,height:1,fontWeight:FontWeight.w800)),
       const Padding(padding:EdgeInsets.only(left:9,bottom:5),child:Text('workout sessions',style:TextStyle(color:Color(0xFFB8C5BE),fontSize:13))),
      ]),const SizedBox(height:18),
      Row(children:List.generate(7,(i){final day=DateTime.now().subtract(Duration(days:6-i));final active=logs.any((w)=>w.workoutDate.year==day.year&&w.workoutDate.month==day.month&&w.workoutDate.day==day.day);
       return Expanded(child:Column(children:[Container(height:7,margin:const EdgeInsets.symmetric(horizontal:4),decoration:BoxDecoration(color:active?lime:Colors.white24,borderRadius:BorderRadius.circular(8))),const SizedBox(height:8),Text(const ['M','T','W','T','F','S','S'][day.weekday-1],style:TextStyle(color:active?lime:Colors.white54,fontSize:10,fontWeight:FontWeight.w700))]));})),
     ])),
    const SizedBox(height:22),const _Heading('YOUR SNAPSHOT','A quick look at your current stats'),const SizedBox(height:12),
    Row(children:[Expanded(child:_Metric('CURRENT WEIGHT',profile?.currentWeightKg?.toStringAsFixed(1)??'—',profile?.currentWeightKg==null?'Add your weight':'kg',Icons.monitor_weight_outlined)),const SizedBox(width:12),Expanded(child:_Metric('GOAL WEIGHT',profile?.goalWeightKg?.toStringAsFixed(1)??'—',profile?.goalWeightKg==null?'Set a target':'kg',Icons.flag_outlined))]),
    const SizedBox(height:12),Row(children:[Expanded(child:_Metric('TODAY', '$today',today==1?'session':'sessions',Icons.today_outlined)),const SizedBox(width:12),Expanded(child:_Metric('TOTAL LOGS',logs.length.toString(),'workout entries',Icons.fitness_center_rounded))]),
    const SizedBox(height:22),const _Heading('RECENT ACTIVITY','Your latest logged exercises'),const SizedBox(height:12),
    if(logs.isEmpty)Container(padding:const EdgeInsets.all(18),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18),border:Border.all(color:const Color(0xFFE5EAE4))),child:const Row(children:[Icon(Icons.sports_gymnastics_rounded,color:muted,size:28),SizedBox(width:12),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text('Your first workout starts here',style:TextStyle(color:ink,fontWeight:FontWeight.w800)),SizedBox(height:4),Text('Log a session to see your training history here.',style:TextStyle(color:muted,fontSize:12))]))]))
    else ...logs.take(3).map((w)=>_WorkoutTile(w)),
    const SizedBox(height:18),Text(email,style:const TextStyle(color:muted,fontSize:11)),
   ]));
  });
 static String _greeting(){final h=DateTime.now().hour;return h<12?'morning':h<17?'afternoon':'evening';}
}
class _Heading extends StatelessWidget{const _Heading(this.title,this.subtitle);final String title,subtitle;@override Widget build(BuildContext context)=>Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(title,style:const TextStyle(color:ink,fontSize:15,fontWeight:FontWeight.w800,letterSpacing:.5)),const SizedBox(height:3),Text(subtitle,style:const TextStyle(color:muted,fontSize:11))]);}
class _Metric extends StatelessWidget{const _Metric(this.label,this.value,this.unit,this.icon);final String label,value,unit;final IconData icon;@override Widget build(BuildContext context)=>Container(padding:const EdgeInsets.all(15),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18),border:Border.all(color:const Color(0xFFE5EAE4))),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Icon(icon,color:const Color(0xFF63805C),size:19),const SizedBox(height:13),Text(label,style:const TextStyle(color:muted,fontSize:9,letterSpacing:1,fontWeight:FontWeight.w800)),const SizedBox(height:5),Text(value,style:const TextStyle(color:ink,fontSize:25,fontWeight:FontWeight.w800)),Text(unit,style:const TextStyle(color:muted,fontSize:10))]));}
class _WorkoutTile extends StatelessWidget{const _WorkoutTile(this.workout);final WorkoutLog workout;@override Widget build(BuildContext context)=>Container(margin:const EdgeInsets.only(bottom:9),padding:const EdgeInsets.all(14),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(16),border:Border.all(color:const Color(0xFFE5EAE4))),child:Row(children:[Container(width:40,height:40,decoration:BoxDecoration(color:const Color(0xFFF0F5E9),borderRadius:BorderRadius.circular(13)),child:const Icon(Icons.fitness_center_rounded,color:Color(0xFF63805C))),const SizedBox(width:12),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(workout.exerciseName,style:const TextStyle(color:ink,fontWeight:FontWeight.w800,fontSize:13)),const SizedBox(height:3),Text(workout.muscleGroup+' · '+workout.sets.length.toString()+' sets',style:const TextStyle(color:muted,fontSize:11))])),Text(workout.workoutDate.day.toString()+'/'+workout.workoutDate.month.toString(),style:const TextStyle(color:muted,fontSize:11))]));}

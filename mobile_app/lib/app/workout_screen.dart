import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../data/repositories/fitness_models.dart';
import '../data/repositories/local_fitness_repository.dart';

const _dark=Color(0xFF17211F), _muted=Color(0xFF75827D), _lime=Color(0xFFB8F36B), _bg=Color(0xFFF3F5F1);

class WorkoutScreen extends StatefulWidget {
 const WorkoutScreen({required this.userId,required this.repository,super.key});
 final String userId; final LocalFitnessRepository repository;
 @override State<WorkoutScreen> createState()=>_WorkoutScreenState();
}
class _WorkoutScreenState extends State<WorkoutScreen> {
 final _exercise=TextEditingController(),_weight=TextEditingController(),_reps=TextEditingController(),_notes=TextEditingController();
 static const _groups=['Chest','Back','Shoulders','Arms','Legs','Core','Cardio','Full Body'];
 String _group='Chest'; int _sets=3; bool _saving=false; String? _error; late Future<List<WorkoutLog>> _logs;
 @override void initState(){super.initState();_refresh();}
 void _refresh(){_logs=widget.repository.getWorkoutLogs(widget.userId);}
 @override void dispose(){_exercise.dispose();_weight.dispose();_reps.dispose();_notes.dispose();super.dispose();}
 Future<void> _save() async {
  final name=_exercise.text.trim(), weight=double.tryParse(_weight.text.trim()), reps=int.tryParse(_reps.text.trim());
  if(name.length<2||weight==null||weight<0||weight>1000||reps==null||reps<1||reps>500){setState(()=>_error='Exercise, valid weight and reps भरें.');return;}
  setState(()=>_saving=true);
  try{final now=DateTime.now().toUtc();await widget.repository.saveWorkout(WorkoutLog(recordId:const Uuid().v4(),userId:widget.userId,workoutDate:now,muscleGroup:_group,exerciseName:name,sets:List.generate(_sets,(_)=>WorkoutSet(weightKg:weight,reps:reps)),notes:_notes.text.trim(),createdAt:now,updatedAt:now));
   if(!mounted)return;_exercise.clear();_weight.clear();_reps.clear();_notes.clear();setState(()=>{_error=null,_saving=false,_refresh()});ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content:Text('Workout saved on this device')));
  }catch(_){if(mounted)setState(()=>{_saving=false,_error='Workout save नहीं हुआ। फिर कोशिश करें।'});}
 }
 @override Widget build(BuildContext context)=>Container(color:_bg,child:ListView(padding:const EdgeInsets.fromLTRB(18,12,18,28),children:[
  Container(padding:const EdgeInsets.all(18),decoration:BoxDecoration(color:_dark,borderRadius:BorderRadius.circular(22)),child:Row(children:[const Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text('TRAIN WITH INTENT',style:TextStyle(color:Color(0xFFB8C5BE),fontSize:10,letterSpacing:1.6,fontWeight:FontWeight.w800)),SizedBox(height:7),Text('Log your workout',style:TextStyle(color:Colors.white,fontSize:22,fontWeight:FontWeight.w800)),SizedBox(height:4),Text('Every rep counts. Keep your progress personal.',style:TextStyle(color:Color(0xFFB8C5BE),fontSize:11))])),Container(width:44,height:44,decoration:BoxDecoration(color:_lime,borderRadius:BorderRadius.circular(14)),child:const Icon(Icons.fitness_center_rounded,color:_dark))])),
  const SizedBox(height:18),const Text('NEW EXERCISE',style:TextStyle(color:_dark,fontSize:13,fontWeight:FontWeight.w800,letterSpacing:.8)),const SizedBox(height:10),
  Container(padding:const EdgeInsets.all(16),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(20),border:Border.all(color:const Color(0xFFE5EAE4))),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
   TextField(controller:_exercise,textCapitalization:TextCapitalization.words,decoration:const InputDecoration(labelText:'Exercise name',hintText:'e.g. Bench Press',prefixIcon:Icon(Icons.edit_outlined))),const SizedBox(height:12),
   DropdownButtonFormField<String>(value:_group,decoration:const InputDecoration(labelText:'Muscle group',prefixIcon:Icon(Icons.category_outlined)),items:_groups.map((g)=>DropdownMenuItem(value:g,child:Text(g))).toList(),onChanged:(v){if(v!=null)setState(()=>_group=v);}),const SizedBox(height:12),
   Row(children:[Expanded(child:TextField(controller:_weight,keyboardType:const TextInputType.numberWithOptions(decimal:true),decoration:const InputDecoration(labelText:'Weight (kg)'))),const SizedBox(width:10),Expanded(child:TextField(controller:_reps,keyboardType:TextInputType.number,decoration:const InputDecoration(labelText:'Reps')))]),const SizedBox(height:14),
   Row(children:[const Expanded(child:Text('Number of sets',style:TextStyle(color:_dark,fontWeight:FontWeight.w700))),IconButton(onPressed:_sets>1?()=>setState(()=>_sets--):null,icon:const Icon(Icons.remove_circle_outline)),Text('$_sets',style:const TextStyle(color:_dark,fontWeight:FontWeight.w800,fontSize:16)),IconButton(onPressed:_sets<10?()=>setState(()=>_sets++):null,icon:const Icon(Icons.add_circle_outline))]),
   TextField(controller:_notes,maxLines:2,decoration:const InputDecoration(labelText:'Notes (optional)',hintText:'How did it feel?')),
   if(_error!=null)Padding(padding:const EdgeInsets.only(top:10),child:Text(_error!,style:const TextStyle(color:Colors.red,fontSize:12))),const SizedBox(height:14),
   SizedBox(width:double.infinity,child:FilledButton.icon(onPressed:_saving?null:_save,icon:_saving?const SizedBox(width:16,height:16,child:CircularProgressIndicator(strokeWidth:2)):const Icon(Icons.save_outlined),label:Text(_saving?'Saving...':'Save workout'),style:FilledButton.styleFrom(backgroundColor:_dark,foregroundColor:Colors.white,padding:const EdgeInsets.symmetric(vertical:15)))),
  ])),
  const SizedBox(height:22),const Text('WORKOUT HISTORY',style:TextStyle(color:_dark,fontSize:13,fontWeight:FontWeight.w800,letterSpacing:.8)),const SizedBox(height:10),
  FutureBuilder<List<WorkoutLog>>(future:_logs,builder:(context,snap){if(snap.connectionState!=ConnectionState.done)return const Center(child:Padding(padding:EdgeInsets.all(20),child:CircularProgressIndicator()));if(snap.hasError)return const Text('History could not be loaded.');final logs=snap.data??[];if(logs.isEmpty)return const Padding(padding:EdgeInsets.all(18),child:Text('No workouts logged yet. Your saved exercises will appear here.',style:TextStyle(color:_muted,fontSize:12)));return Column(children:logs.take(30).map((w)=>Container(margin:const EdgeInsets.only(bottom:9),padding:const EdgeInsets.all(14),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(16),border:Border.all(color:const Color(0xFFE5EAE4))),child:Row(children:[Container(width:40,height:40,decoration:BoxDecoration(color:const Color(0xFFF0F5E9),borderRadius:BorderRadius.circular(12)),child:const Icon(Icons.fitness_center,color:Color(0xFF63805C))),const SizedBox(width:12),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(w.exerciseName,style:const TextStyle(color:_dark,fontWeight:FontWeight.w800)),const SizedBox(height:3),Text(w.muscleGroup+' · '+w.sets.length.toString()+' sets · '+w.sets.first.weightKg.toString()+' kg × '+w.sets.first.reps.toString(),style:const TextStyle(color:_muted,fontSize:11))])),Text(w.workoutDate.day.toString()+'/'+w.workoutDate.month.toString(),style:const TextStyle(color:_muted,fontSize:11))])).toList());}),
 ]));
}
